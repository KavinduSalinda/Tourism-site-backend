from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import date, time
import json
from decouple import config
from booking.models import Destination, Vehicle, VehicleDestinationPrice, Booking
from customer.models import Customer
from utils.email import send_email
from django.conf import settings


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
                    'image_url': destination.image.url if destination.image else None
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
                        'image_url': destination.image.url if destination.image else None,
                        'distance': destination.distance,
                        'duration': destination.duration,
                        'latitude': destination.latitude,
                        'longitude': destination.longitude
                    
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




class VehicleListView(View):
    """Get vehicles with destination-specific pricing or all vehicles if no destination_id provided"""
   
    def get(self, request):
        try:
            destination_id = request.GET.get('destination_id')
            
            if not destination_id:
                vehicles = Vehicle.objects.all()
                vehicles_data = []
                
                for vehicle in vehicles:
                    vehicle_info = {
                        'id': vehicle.id,
                        'type': vehicle.type,
                        'type_display': vehicle.get_type_display(),
                        'capacity': vehicle.capacity,
                        'image': vehicle.image.url if vehicle.image else None,
                    }
                    vehicles_data.append(vehicle_info)

                return JsonResponse({
                    'data': vehicles_data,
                    'destination': None,
                    'message': 'All vehicles fetched successfully',
                    'status': 200
                })

            pricing_queryset = VehicleDestinationPrice.objects.filter(
                destination_id=destination_id
            ).select_related('vehicle', 'destination')

            vehicles_data = []
            destination_info = None
            
            for pricing in pricing_queryset:
                vehicle_info = {
                    'id': pricing.vehicle.id,
                    'type': pricing.vehicle.type,
                    'capacity': pricing.vehicle.capacity,
                    'price': float(pricing.price),
                    'image_url': pricing.vehicle.image
                }
                vehicles_data.append(vehicle_info)
                
                if not destination_info:
                    destination_info = {
                        'id': pricing.destination.id,
                        'name': pricing.destination.name
                    }

            return JsonResponse({
                'data': vehicles_data,
                'destination': destination_info,
                'message': 'Vehicles fetched successfully',
                'status': 200
            })

        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error fetching vehicles','status':500})


class TripDetailsView(View):
    """Get trip details based on distance table"""
    
    def get(self, request, booking_id=None):
        try:
            if booking_id:
                booking = get_object_or_404(Booking, id=booking_id)
                if not booking.destination:
                    return JsonResponse({
                        'data': None,
                        'message': 'No destination associated with this booking',
                        'status': 404
                    }, status=404)
                
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

            return JsonResponse({
                'data': [],
                'destination': None,
                'message': str(e),
                'status': 500
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PriceDetailView(View):
    """Get prices for vehicle-destination combinations"""
    
    def get(self, request):
        try:
            # Get query parameters
            vehicle_id = request.GET.get('vehicle_id')
            destination_id = request.GET.get('destination_id')
            
            # Start with all prices
            prices = VehicleDestinationPrice.objects.select_related('vehicle', 'destination')
            
            # Filter by vehicle_id if provided
            if vehicle_id:
                try:
                    vehicle_id = int(vehicle_id)
                    prices = prices.filter(vehicle_id=vehicle_id)
                except ValueError:
                    return JsonResponse({'error': 'Invalid vehicle_id', 'message': 'vehicle_id must be a number', 'status': 400})
            
            # Filter by destination_id if provided
            if destination_id:
                try:
                    destination_id = int(destination_id)
                    prices = prices.filter(destination_id=destination_id)
                except ValueError:
                    return JsonResponse({'error': 'Invalid destination_id', 'message': 'destination_id must be a number', 'status': 400})
            
            data = []
            for price_obj in prices:
                data.append({
                    'id': price_obj.id,
                    'vehicle_id': price_obj.vehicle.id,
                    'vehicle_type': price_obj.vehicle.get_type_display(),
                    'destination_id': price_obj.destination.id,
                    'destination_name': price_obj.destination.name,
                    'price': float(price_obj.price)
                })
            
            if not data:
                return JsonResponse({'data': [], 'message': 'No prices found for the specified criteria', 'status': 404})
            
            return JsonResponse({'data': data, 'message': 'Prices fetched successfully', 'status': 200})
        except Exception as e:
            return JsonResponse({'error': str(e), 'message': 'Error fetching prices', 'status': 500})


class BookingCreateView(View):
    """Create a new booking with customer"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields for customer
            customer_required_fields = ['first_name', 'last_name', 'email']
            for field in customer_required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field} is required','message': f'{field} is required','status':400})
            
            # Validate required fields for booking
            booking_required_fields = ['no_of_passengers', 'pickup_date', 'pickup_time']
            for field in booking_required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'{field} is required','message': f'{field} is required','status':400})
            
            # Handle optional vehicle_id
            vehicle = None
            if 'vehicle_id' in data and data['vehicle_id']:
                try:
                    vehicle = get_object_or_404(Vehicle, id=data['vehicle_id'])
                except (ValueError, Vehicle.DoesNotExist):
                    return JsonResponse({'error': 'Invalid vehicle_id','message': 'Invalid vehicle_id','status':400})
            
            # Handle optional destination_id
            destination = None
            if 'destination_id' in data and data['destination_id']:
                try:
                    destination = get_object_or_404(Destination, id=data['destination_id'])
                except (ValueError, Destination.DoesNotExist):
                    return JsonResponse({'error': 'Invalid destination_id','message': 'Invalid destination_id','status':400})
            
            # Get price only if both vehicle and destination are provided
            price_obj = None
            if vehicle and destination:
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
            
            # Create customer with optional fields
            customer_data = {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'phone_no': data.get('phone_no', ''),  # Optional
                'country': data.get('country', ''),     # Optional
                'message': data.get('message', '')
            }
            customer = Customer.objects.create(**customer_data)
            
            # Create booking with optional fields
            booking_data = {
                'customer': customer,
                'no_of_passengers': data['no_of_passengers'],
                'pickup_date': pickup_date,
                'pickup_time': pickup_time,
                'pickup_location': data.get('pickup_location', ''),
                'dropoff_location': data.get('dropoff_location', ''),
                'additional_info': data.get('additional_info', ''),
                'is_return_trip': data.get('is_return_trip', False)
            }
            
            # Add vehicle and destination if provided
            if vehicle:
                booking_data['vehicle'] = vehicle
            if destination:
                booking_data['destination'] = destination
            if price_obj:
                booking_data['vehicle_destination_price'] = price_obj
            
            booking = Booking.objects.create(**booking_data)

            # Send email to admin
            recipients = [(settings.ADMIN_EMAIL, "Admin")]
            params = {
                "user_name": booking.customer.first_name + ' ' + booking.customer.last_name,
                "destination": booking.destination.name if booking.destination else 'Not specified',
                "vehicle": booking.vehicle.type if booking.vehicle else 'Not specified',
                "pickup_date": str(booking.pickup_date),
                "pickup_time": str(booking.pickup_time),
                "no_of_passengers": booking.no_of_passengers,
                "price": booking.vehicle_destination_price.price if booking.vehicle_destination_price else 'Not specified',
                "customer": booking.customer.first_name + ' ' + booking.customer.last_name,
            }

            # send email to admin
            send_email(template_id=2, recipients=recipients, params=params)

            return JsonResponse({'message': 'Booking created successfully','status':201})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON','message': 'Invalid JSON','status':400})
        except Exception as e:
            return JsonResponse({'error': str(e),'message': 'Error creating booking','status':500})
