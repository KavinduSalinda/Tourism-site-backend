from django.contrib import admin
from .models import Destination, Vehicle, VehicleDestinationPrice, Booking


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'distance', 'duration', 'latitude', 'longitude']
    search_fields = ['name']
    list_filter = ['duration']
    ordering = ['name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'distance', 'duration')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['type', 'capacity']
    list_filter = ['type']
    ordering = ['type']
    search_fields = ['type']


@admin.register(VehicleDestinationPrice)
class VehicleDestinationPriceAdmin(admin.ModelAdmin):
    list_display = ['get_vehicle_type_and_price', 'destination']
    list_filter = ['vehicle', 'destination']
    search_fields = ['vehicle__type', 'destination__name']
    ordering = ['vehicle', 'destination']
    
    def get_vehicle_type_and_price(self, obj):
        return f"{obj.vehicle.get_type_display()} - ${obj.price}"
    get_vehicle_type_and_price.short_description = 'Vehicle and Price'
    

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'vehicle_type_and_price', 'destination_name', 'no_of_passengers', 'pickup_date', 'pickup_time', 'is_return_trip', 'created_at']
    list_filter = ['is_return_trip', 'created_at', 'vehicle', 'destination', 'pickup_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    
    def vehicle_type_and_price(self, obj):
        return f"{obj.vehicle.get_type_display()} - ${obj.vehicle_destination_price.price}"
    vehicle_type_and_price.short_description = 'Vehicle and Price'
    
    def destination_name(self, obj):
        return obj.destination.name
    destination_name.short_description = 'Destination'
