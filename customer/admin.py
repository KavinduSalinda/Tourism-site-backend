from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Testimonial,Message,Newsletter



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone_no', 'country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['country', 'created_at']
    ordering = ['first_name', 'last_name']
    list_per_page = 25
    date_hierarchy = 'created_at'
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
    list_display = ['customer_name', 'country', 'profile_icon_preview', 'review_preview', 'created_at']
    search_fields = ['customer_name', 'country', 'review']
    list_filter = ['country', 'created_at']
    ordering = ['-created_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'country', 'profile_icon')
        }),
        ('Review', {
            'fields': ('review',)
        }),
    )
    
    def profile_icon_preview(self, obj):
        if obj.profile_icon:
            return format_html('<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 50%;" />', obj.profile_icon.url)
        return "No icon"
    profile_icon_preview.short_description = 'Profile Icon'
    
    def review_preview(self, obj):
        return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
    review_preview.short_description = 'Review Preview'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    search_fields = ['email']
    list_filter = ['created_at']
    ordering = ['-created_at']
    fieldsets = (
        ('Newsletter Information', {
            'fields': ('email',)
        }),

    )