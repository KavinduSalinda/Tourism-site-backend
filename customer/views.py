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
import http.client

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


class SubscribeNewsletterView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        headers = {
            'Content-Type': 'application/json',
            'api-key': settings.SENDINBLUE_API_KEY, # Make sure this matches your settings.py
        }

        # 1. ADD THIS REQUIRED FIELD TO THE PAYLOAD
        payload = {
            'email': email,
            'templateId':int(settings.BREVO_DOI_TEMPLATE_ID),
            'redirectionUrl': settings.BREVO_REDIRECT_URL,
            'includeListIds': [int(settings.BREVO_CONTACT_LIST_ID)]
        }

        try:
            conn = http.client.HTTPSConnection('api.brevo.com')
            conn.request('POST', '/v3/contacts/doubleOptinConfirmation', json.dumps(payload), headers)
            res = conn.getresponse()
            
            # 2. CHECK FOR ANY 2xx SUCCESS CODE
            if not (200 <= res.status < 300): # <--- THIS FIXES THE 500 ERROR
                response_data = res.read().decode()
                # Raise an exception with details from Brevo's response
                raise Exception(f"Error: {res.status} - {res.reason}. Response: {response_data}")

            return JsonResponse({'success': 'Confirmation email sent!'}, status=201)

        except Exception as e:
            print(f"Error calling Brevo API: {e}")
            return JsonResponse({'error': 'Failed to subscribe. Please try again later.'}, status=500)