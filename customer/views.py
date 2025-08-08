from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
from .models import Customer, Testimonial,Message
from django.conf import settings
from utils.email import send_email


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
            
            # Check if customer already exists by email
            try:
                customer = Customer.objects.get(email=data['email'])
                # Update customer information if it has changed
                customer.first_name = data['first_name']
                customer.last_name = data['last_name']
                customer.phone_no = data['phone_no']
                customer.country = data['country']
                customer.save()
            except Customer.DoesNotExist:
                # Create new customer if they don't exist
                customer = Customer.objects.create(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    phone_no=data['phone_no'],
                    country=data['country']
                )
            
            # Create the message
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
            send_email(template_id=4, recipients=recipients, params=params)
            
            return JsonResponse({'message': 'Contact message created successfully','status':201})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error creating contact message','status':500})



