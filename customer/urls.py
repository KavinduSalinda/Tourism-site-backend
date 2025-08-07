from django.urls import path
from . import views


urlpatterns = [
    # Testimonial endpoints
    path('api/testimonials/', views.TestimonialListView.as_view(), name='testimonial_list'),
    
    # Contact creation endpoint
    path('api/contact-us/', views.ContactCreateView.as_view(), name='contact_create'),

    #newsletter endpoints
    path('api/newsletter/', views.SubscribeNewsletterView.as_view(), name='newsletter_create'),
] 