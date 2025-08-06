from django.urls import path
from . import views


urlpatterns = [
    # Testimonial endpoints
    path('api/testimonials/', views.TestimonialListView.as_view(), name='testimonial_list'),
    
    # Contact creation endpoint
    path('api/contact-us/', views.ContactCreateView.as_view(), name='contact_create'),

    #newsletter endpoints
    path('api/newsletter/', views.NewsletterCreateView.as_view(), name='newsletter_create'),
    path('api/newsletter/verify/<uuid:token>/', views.NewsletterVerifyView.as_view(), name='newsletter_verify'),
    path('api/newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
] 