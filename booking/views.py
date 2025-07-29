from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, date, time
import json
from .models import Destination, Vehicle, VehicleDestinationPrice, Booking
from customer.models import Customer


@method_decorator(csrf_exempt, name='dispatch')
class DestinationListView(View):
    """View for handling destination operations"""
    
    def get(self, request, destination_id=None):
        """Get all destinations or a specific destination by ID"""
        try:
            if destination_id:
                # Get specific destination by ID
                destination = get_object_or_404(Destination, id=destination_id)
                destination_data = {
                    'id': destination.id,
                    'name': destination.name,
                    'description': destination.description,
                    'image_url': destination.image
                }
                
                return JsonResponse({
                    'data': destination_data,
                    'message': 'Destination fetched successfully',
                    'status': 200
                })
            else:
                # Get all destinations
                destinations = Destination.objects.all()
                destinations_data = []
                
                for destination in destinations:
                    destinations_data.append({
                        'id': destination.id,
                        'name': destination.name,
                        'description': destination.description,
                        'image_url': destination.image  
                    })
                
                return JsonResponse({
                    'data': destinations_data,  
                    'message': 'Destinations fetched successfully', 
                    'status': 200  
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class VehicleListView(View):
    """Get all vehicles"""
    
    def get(self, request):
        try:
            vehicles = Vehicle.objects.all()
            data = []
            for vehicle in vehicles:
                data.append({
                    'id': vehicle.id,
                    'type': vehicle.type,
                    'type_display': vehicle.get_type_display(),
                    'capacity': vehicle.capacity
                })
            return JsonResponse({ 'data': data ,'message': 'Vehicles fetched successfully','status':200})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error fetching vehicles','status':500})




@method_decorator(csrf_exempt, name='dispatch')
class TripDetailsView(View):
    """Get trip details based on distance table"""
    
    def get(self, request, booking_id=None):
        try:
            if booking_id:
                booking = get_object_or_404(Booking, id=booking_id)
                trip_data = {
                    'id': booking.destination.id,
                    'name': booking.destination.name,
                    'distance': float(booking.destination.distance) if booking.destination.distance else None,
                    'duration': booking.destination.duration,
                    'latitude': float(booking.destination.latitude) if booking.destination.latitude else None,
                    'longitude': float(booking.destination.longitude) if booking.destination.longitude else None,
                }
                
                return JsonResponse({
                    'data': trip_data,
                    'message': 'Trip Details fetched successfully',
                    'status': 200
                })
            
            else:
                destination_id = request.GET.get('destination_id')
                if not destination_id:
                    return JsonResponse({
                        'data': None,
                        'message': 'destination_id parameter is required',
                        'status': 400
                    }, status=400)
                
                destination = get_object_or_404(Destination, id=destination_id)
                destination_data = {
                    'id': destination.id,
                    'name': destination.name,
                    'distance': float(destination.distance) if destination.distance else None,
                    'duration': destination.duration,
                    'latitude': float(destination.latitude) if destination.latitude else None,
                    'longitude': float(destination.longitude) if destination.longitude else None,
                }
                
                return JsonResponse({
                    'data': destination_data,
                    'message': 'Trip Details fetched successfully',
                    'status': 200
                })
                
        except Exception as e:
            return JsonResponse({
                'data': None,
                'message': str(e),
                'status': 500
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BookingCreateView(View):
    """Create a new booking with customer"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields for customer
            customer_fields = ['first_name', 'last_name', 'email', 'phone_no', 'country']
            for field in customer_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field} is required','message': f'{field} is required','status':400})
            
            # Validate required fields for booking
            booking_fields = ['vehicle_id', 'destination_id', 'no_of_passengers', 'pickup_date', 'pickup_time']
            for field in booking_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field} is required','message': f'{field} is required','status':400})
            
            # Get related objects
            vehicle = get_object_or_404(Vehicle, id=data['vehicle_id'])
            destination = get_object_or_404(Destination, id=data['destination_id'])
            
            # Get price
            try:
                price_obj = VehicleDestinationPrice.objects.get(vehicle=vehicle, destination=destination)
            except VehicleDestinationPrice.DoesNotExist:
                return JsonResponse({'error': 'Price not available for this combination','message': 'Price not available for this combination','status':400})
            
            # Parse pickup_date
            try:
                pickup_date = date.fromisoformat(data['pickup_date'])
            except ValueError:
                return JsonResponse({'error': 'Invalid pickup_date format. Use ISO format (YYYY-MM-DD)','message': 'Invalid pickup_date format','status':400})
            
            # Parse pickup_time
            try:
                pickup_time = time.fromisoformat(data['pickup_time'])
            except ValueError:
                return JsonResponse({'error': 'Invalid pickup_time format. Use ISO format (HH:MM:SS)','message': 'Invalid pickup_time format','status':400})
            
            # Create customer
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_no=data['phone_no'],
                country=data['country'],
                message=data.get('message', '')
            )
            
            # Create booking
            booking = Booking.objects.create(
                customer=customer,
                vehicle=vehicle,
                destination=destination,
                vehicle_destination_price=price_obj,
                no_of_passengers=data['no_of_passengers'],
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                additional_info=data.get('additional_info', ''),
                is_return_trip=data.get('is_return_trip', False)
            )
            
            return JsonResponse({'message': 'Booking created successfully','status':201})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error creating booking','status':500})


