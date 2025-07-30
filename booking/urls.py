from django.urls import path
from . import views 




urlpatterns = [
    # Destination endpoints
    path('api/destinations/', views.DestinationListView.as_view(), name='destination_list'),
    path('api/destinations/<int:destination_id>/', views.DestinationListView.as_view(), name='destination_detail'),
    
    # Vehicle endpoints
    path('api/vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    
    # Price endpoints

    path('api/prices/<int:price_id>/', views.PriceDetailView.as_view(), name='price_detail'),
    
    # Booking creation endpoint
    path('api/bookings/', views.BookingCreateView.as_view(), name='booking_create'),
]