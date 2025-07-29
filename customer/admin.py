from django.contrib import admin
from .models import Customer, Testimonial,Message



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_no', 'country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['country']
    ordering = ['first_name', 'last_name']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_no', 'country')
        }),
    )
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['customer', 'message', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'message']
    list_filter = ['created_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Message', {
            'fields': ('message',)
        }),
    )

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'country', 'review_preview', 'created_at']
    search_fields = ['customer_name', 'country', 'review']
    list_filter = ['country', 'created_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'country', 'profile_icon')
        }),
        ('Review', {
            'fields': ('review',)
        }),
    )
    
    def review_preview(self, obj):
        return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
    review_preview.short_description = 'Review Preview'
