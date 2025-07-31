from django.db import models
from customer.models import Customer


class Destination(models.Model):
    name = models.CharField(max_length=200)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='destination_images/')
    
    def __str__(self):
        return self.name


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('sedan', 'Sedan'),
        ('wagon R', 'Wagon R'),
        ('van', 'Van'),
    ]
    
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    capacity = models.IntegerField(help_text="Number of passengers")
    image = models.ImageField(upload_to='vehicle_images/')
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.capacity} passengers"


class VehicleDestinationPrice(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['vehicle', 'destination']
    
    def __str__(self):
        return f"{self.vehicle} to {self.destination} - ${self.price}"


class Booking(models.Model):
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    vehicle_destination_price = models.ForeignKey(VehicleDestinationPrice, on_delete=models.CASCADE)
    no_of_passengers = models.IntegerField()
    pickup_location = models.CharField(max_length=200, null=True, blank=True)
    dropoff_location = models.CharField(max_length=200, null=True, blank=True)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    additional_info = models.TextField(blank=True)
    is_return_trip = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.customer} to {self.destination}"