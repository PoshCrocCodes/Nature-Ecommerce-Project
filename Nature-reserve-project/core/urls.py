from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('terms/', views.terms_and_conditions, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('api/cookie-consent/', views.set_cookie_consent, name='set_cookie_consent'),
]
