from django.urls import path
from . import views

urlpatterns = [
    path('', views.newsletter_signup, name='newsletter_signup'),
    path('success/', views.success, name="success"),
    path('failure/', views.failure, name='failure'),
]