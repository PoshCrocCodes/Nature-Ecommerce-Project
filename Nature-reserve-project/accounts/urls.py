from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.producer_dashboard, name='producer_dashboard'),
    path('dashboard/product/<int:product_id>/update/', views.update_product_quick, name='update_product_quick'),
]
