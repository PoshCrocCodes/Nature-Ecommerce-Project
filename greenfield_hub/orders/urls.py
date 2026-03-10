from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.order_list, name='order_list'),
    path('track/<str:tracking_code>/', views.order_tracking, name='order_tracking'),
    path('status/<str:tracking_code>/', views.get_order_status, name='get_order_status'),
]
