from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from products.models import Product
from .models import Order, OrderItem, Cart, CartItem
import json


# ─── CART VIEWS (session-based, works for all users) ───────────────────────

def cart_view(request):
    """Display the shopping cart."""
    cart_data = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            subtotal += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass

    delivery_fee = 3.99 if subtotal > 0 else 0
    grand_total = subtotal + delivery_fee

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Add a product to the session cart."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1
    if quantity > product.stock:
        quantity = product.stock

    cart = request.session.get('cart', {})
    key = str(product_id)

    new_qty = cart.get(key, 0) + quantity
    if new_qty > product.stock:
        new_qty = product.stock

    cart[key] = new_qty
    request.session['cart'] = cart
    request.session.modified = True

    cart_count = sum(cart.values())

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': f'"{product.name}" added to cart!'
        })

    messages.success(request, f'"{product.name}" added to your cart!')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@require_POST
def update_cart(request, product_id):
    """Update quantity in session cart."""
    cart = request.session.get('cart', {})
    key = str(product_id)
    quantity = int(request.POST.get('quantity', 0))

    if quantity <= 0:
        cart.pop(key, None)
    else:
        try:
            product = Product.objects.get(id=product_id)
            cart[key] = min(quantity, product.stock)
        except Product.DoesNotExist:
            cart.pop(key, None)

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


@require_POST
def remove_from_cart(request, product_id):
    """Remove a product from the session cart."""
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ─── CHECKOUT ────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    """Checkout page - requires login."""
    cart_data = request.session.get('cart', {})
    if not cart_data:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    cart_items = []
    subtotal = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if quantity > product.stock:
                quantity = product.stock
            item_total = product.price * quantity
            subtotal += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass

    profile = request.user.profile
    delivery_fee = 3.99

    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method', 'delivery')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_city = request.POST.get('delivery_city', '')
        delivery_postcode = request.POST.get('delivery_postcode', '')
        notes = request.POST.get('notes', '')
        scheduled_date = request.POST.get('scheduled_date', '')
        scheduled_time = request.POST.get('scheduled_time', '')

        if delivery_method == 'delivery' and not delivery_address:
            messages.error(request, 'Please provide a delivery address.')
            return redirect('checkout')

        # Parse scheduled delivery
        scheduled_delivery = None
        if scheduled_date and scheduled_time:
            try:
                from datetime import datetime
                scheduled_delivery = datetime.strptime(
                    f'{scheduled_date} {scheduled_time}', '%Y-%m-%d %H:%M'
                )
                scheduled_delivery = timezone.make_aware(scheduled_delivery)
            except ValueError:
                pass

        # Calculate fees
        actual_delivery_fee = 0 if delivery_method == 'collection' else delivery_fee

        # Create the order
        order = Order.objects.create(
            user=request.user,
            delivery_method=delivery_method,
            delivery_address=delivery_address,
            delivery_city=delivery_city,
            delivery_postcode=delivery_postcode,
            notes=notes,
            total_price=subtotal,
            delivery_fee=actual_delivery_fee,
            scheduled_delivery=scheduled_delivery,
            status='pending',
        )

        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                quantity=item['quantity'],
                price=item['product'].price,
            )
            # Reduce stock
            product = item['product']
            product.stock = max(0, product.stock - item['quantity'])
            product.save()

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f'Order placed successfully! Your tracking code is {order.tracking_code}')
        return redirect('order_tracking', tracking_code=order.tracking_code)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'grand_total': subtotal + delivery_fee,
        'profile': profile,
    }
    return render(request, 'orders/checkout.html', context)


# ─── ORDER TRACKING ──────────────────────────────────────────────────────────

def order_tracking(request, tracking_code):
    """
    Order tracking page with animated progress bar.
    The status is stored in the database and can be manually updated by admin
    or via the simulated progression script below.
    """
    order = get_object_or_404(Order, tracking_code=tracking_code)

    # Only allow the order owner or staff to view
    if request.user != order.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('home')

    statuses = [
        {'key': 'pending', 'label': 'Order Placed', 'icon': '🛒', 'description': 'We have received your order'},
        {'key': 'confirmed', 'label': 'Confirmed', 'icon': '✅', 'description': 'Your order is confirmed and being processed'},
        {'key': 'preparing', 'label': 'Preparing', 'icon': '🌿', 'description': 'Our producers are preparing your fresh items'},
        {'key': 'ready', 'label': 'Ready', 'icon': '📦', 'description': 'Your order is packed and ready'},
        {'key': 'out_for_delivery', 'label': 'Out for Delivery', 'icon': '🚚', 'description': 'Your order is on its way!'},
        {'key': 'delivered', 'label': 'Delivered', 'icon': '🏡', 'description': 'Order delivered - enjoy your produce!'},
    ]

    context = {
        'order': order,
        'statuses': statuses,
        'current_step': order.status_step,
        'progress_percentage': order.status_percentage,
    }
    return render(request, 'orders/order_tracking.html', context)


@login_required
def order_list(request):
    """List all orders for the current user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


def get_order_status(request, tracking_code):
    """AJAX endpoint to get current order status for live updates."""
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if request.user != order.user and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorised'}, status=403)

    return JsonResponse({
        'status': order.status,
        'status_display': order.get_status_display(),
        'status_step': order.status_step,
        'progress_percentage': order.status_percentage,
    })
