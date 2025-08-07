from django.contrib import admin
from django.utils.html import format_html
from .models import Destination, Vehicle, VehicleDestinationPrice, Booking


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'distance', 'duration', 'latitude', 'longitude', 'image_preview']
    search_fields = ['name']
    list_filter = ['duration']
    ordering = ['name']
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'distance', 'duration', 'image')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'image_preview']
    list_filter = ['capacity']
    ordering = ['name']
    search_fields = ['name']
    list_per_page = 20
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image'


@admin.register(VehicleDestinationPrice)
class VehicleDestinationPriceAdmin(admin.ModelAdmin):
    list_display = ['get_vehicle_name_and_price', 'destination']
    list_filter = ['vehicle', 'destination']
    search_fields = ['vehicle__name', 'destination__name']
    ordering = ['vehicle', 'destination']
    
    def get_vehicle_name_and_price(self, obj):
        return f"{obj.vehicle.name} - ${obj.price}"
    get_vehicle_name_and_price.short_description = 'Vehicle and Price'
    

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'vehicle_name_and_price', 'pickup_location_display', 'dropoff_location_display', 'no_of_passengers', 'pickup_date', 'pickup_time', 'status', 'additional_info', 'created_at_display']
    list_filter = ['is_return_trip', 'created_at', 'vehicle', 'destination', 'pickup_date', 'status']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email', 'customer__phone_no']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'no_of_passengers')
        }),
        ('Trip Details', {
            'fields': ('vehicle', 'destination', 'vehicle_destination_price', 'pickup_location', 'dropoff_location', 'pickup_date', 'pickup_time', 'is_return_trip')
        }),
        ('Additional Information', {
            'fields': ('additional_info', 'status')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"
    customer_name.short_description = 'Customer'
    
    def vehicle_name_and_price(self, obj):
        if obj.vehicle and obj.vehicle_destination_price:
            return f"{obj.vehicle.name} - ${obj.vehicle_destination_price.price}"
        elif obj.vehicle:
            return f"{obj.vehicle.name} - No price set"
        else:
            return "No vehicle selected"
    vehicle_name_and_price.short_description = 'Vehicle and Price'
    
    def pickup_location_display(self, obj):
        """Show pickup location based on return trip logic"""
        if obj.destination:
            if obj.is_return_trip:
                return obj.destination.name
            else:
                return "Negombo"
        else:
            return obj.pickup_location or ""
    pickup_location_display.short_description = 'Pickup Location'
    
    def dropoff_location_display(self, obj):
        """Show dropoff location based on return trip logic"""
        if obj.destination:
            if obj.is_return_trip:
                return "Negombo"
            else:
                return obj.destination.name
        else:
            return obj.dropoff_location or ""
    dropoff_location_display.short_description = 'Dropoff Location'
    
    def created_at_display(self, obj):
        """Display created_at as 'Booked At'"""
        return obj.created_at
    created_at_display.short_description = 'Booked At'    
    def customer_email(self, obj):
        return obj.customer.email if obj.customer else "No customer"
    customer_email.short_description = 'Customer Email'
    
    def customer_phone(self, obj):
        return obj.customer.phone_no if obj.customer else "No phone"
    customer_phone.short_description = 'Customer Phone'
