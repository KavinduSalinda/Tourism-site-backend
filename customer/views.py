from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import Customer, Testimonial,Message,Newsletter
from django.conf import settings
from utils.email import send_email
from utils.brevo_contacts import add_contact_to_brevo, update_contact_in_brevo


class TestimonialListView(View):
    """Get all testimonials"""
    
    def get(self, request):
        try:
            testimonials = Testimonial.objects.all().order_by('-created_at')
            data = []
            for testimonial in testimonials:
                data.append({
                    'id': testimonial.id,
                    'customer_name': testimonial.customer_name,
                    'country': testimonial.country,
                    'profile_icon': testimonial.profile_icon.url if testimonial.profile_icon else None,
                    'review': testimonial.review,
                    'created_at': testimonial.created_at.isoformat()
                })
            return JsonResponse({'data': data,'message': 'Testimonials fetched successfully','status':200})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error fetching testimonials','status':500})



class ContactCreateView(View):
    """Create a new contact message"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'phone_no', 'country', 'message']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field} is required','message': f'{field} is required','status':400})
            
            # Create customer with message (using Customer model instead of Contact)
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_no=data['phone_no'],
                country=data['country']
            )
            message = Message.objects.create(
                customer=customer,
                message=data['message']
            )

            # send email to admin
            recipients = [(settings.ADMIN_EMAIL, "Admin")]
            params = {
                "user_name": customer.first_name + ' ' + customer.last_name,
                "message": data['message'],
                "email": customer.email if customer.email else 'Not specified',
                "phone_no": customer.phone_no if customer.phone_no else 'Not specified',
            }
            send_email(template_id=3, recipients=recipients, params=params)
            
            return JsonResponse({'message': 'Contact message created successfully','status':201})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error creating contact message','status':500})


class NewsletterCreateView(View):
    """Create a new newsletter subscription"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required','message': 'Email is required','status':400}) 

            # Check if email already exists
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            
            if not created and newsletter.is_verified:
                return JsonResponse({'message': 'Email already subscribed and verified','status':200})
            
            if not created and not newsletter.is_verified:
                # Resend verification email
                self._send_verification_email(newsletter)
                return JsonResponse({'message': 'Verification email sent again','status':200})
            
            # Send verification email for new subscription
            self._send_verification_email(newsletter)
            
            return JsonResponse({'message': 'Newsletter subscription created successfully. Please check your email for verification.','status':201})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error creating newsletter subscription','status':500})
    
    def _send_verification_email(self, newsletter):
        """Send verification email to newsletter subscriber"""
        try:
            # Generate verification URL
            verification_url = f"{settings.SITE_URL}/api/newsletter/verify/{newsletter.verification_token}"
            
            # Send verification email
            recipients = [(newsletter.email, "Newsletter Subscriber")]
            params = {
                "email": newsletter.email,
                "verification_url": verification_url,
                "site_name": "Vehicle Booking Site"
            }
            
            # Use template ID for newsletter verification (you'll need to create this template in Brevo)
            send_email(template_id=2, recipients=recipients, params=params)
            
        except Exception as e:
            print(f"Error sending verification email: {e}")


class NewsletterVerifyView(View):
    """Verify newsletter subscription"""
    
    def get(self, request, token):
        try:
            # Find newsletter subscription by token
            newsletter = get_object_or_404(Newsletter, verification_token=token, is_verified=False)
            
            # Mark as verified
            newsletter.is_verified = True
            newsletter.verified_at = timezone.now()
            newsletter.save()
            
            # Add to Brevo contact list
            if settings.SEND_EMAIL and settings.SENDINBLUE_API_KEY:
                attributes = {
                    "SUBSCRIPTION_DATE": newsletter.created_at.strftime("%Y-%m-%d"),
                    "VERIFICATION_DATE": newsletter.verified_at.strftime("%Y-%m-%d"),
                    "SOURCE": "Website Newsletter"
                }
                add_contact_to_brevo(newsletter.email, attributes)
            
            return JsonResponse({
                'message': 'Email verified successfully! You are now subscribed to our newsletter.',
                'status': 200
            })
            
        except Newsletter.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid or expired verification link',
                'message': 'Invalid or expired verification link',
                'status': 400
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'message': 'Error verifying newsletter subscription',
                'status': 500
            })


class NewsletterUnsubscribeView(View):
    """Unsubscribe from newsletter"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': 'Email is required','message': 'Email is required','status':400})
            
            # Find and delete newsletter subscription
            try:
                newsletter = Newsletter.objects.get(email=email)
                newsletter.delete()
                
                # Note: You might want to also remove from Brevo contact list
                # This would require additional Brevo API call
                
                return JsonResponse({'message': 'Successfully unsubscribed from newsletter','status':200})
            except Newsletter.DoesNotExist:
                return JsonResponse({'message': 'Email not found in newsletter subscriptions','status':200})
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error unsubscribing from newsletter','status':500})
