from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
from .models import UserProfile
from products.models import Product
from orders.models import Order


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Greenfield, {user.first_name}! Your account has been created.')
            if user.profile.is_producer():
                return redirect('producer_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            if user.profile.is_producer():
                return redirect('producer_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User model fields
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        )

    # Get user's recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'recent_orders': recent_orders,
    })


@login_required
def producer_dashboard(request):
    """Dashboard exclusively for producers to manage their products."""
    if not request.user.profile.is_producer():
        messages.error(request, 'Access denied. This dashboard is for producers only.')
        return redirect('home')

    products = Product.objects.filter(producer=request.user).order_by('-updated_at')

    # Quick stats
    total_products = products.count()
    active_products = products.filter(is_active=True).count()
    low_stock = products.filter(stock__lte=5, is_active=True).count()
    out_of_stock = products.filter(stock=0).count()

    # Recent orders containing producer's products
    from orders.models import OrderItem
    recent_order_items = OrderItem.objects.filter(
        product__producer=request.user
    ).select_related('order', 'product').order_by('-order__created_at')[:10]

    context = {
        'products': products,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'recent_order_items': recent_order_items,
    }
    return render(request, 'accounts/producer_dashboard.html', context)


@login_required
def update_product_quick(request, product_id):
    """AJAX endpoint for producers to quickly update stock/price from dashboard."""
    if not request.user.profile.is_producer():
        from django.http import JsonResponse
        return JsonResponse({'error': 'Unauthorised'}, status=403)

    product = get_object_or_404(Product, id=product_id, producer=request.user)

    if request.method == 'POST':
        import json
        from django.http import JsonResponse
        data = json.loads(request.body)
        field = data.get('field')
        value = data.get('value')

        if field == 'price':
            try:
                product.price = float(value)
                product.save()
                return JsonResponse({'success': True, 'value': str(product.price)})
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid price'}, status=400)
        elif field == 'stock':
            try:
                product.stock = int(value)
                product.save()
                return JsonResponse({'success': True, 'value': product.stock})
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid stock value'}, status=400)
        elif field == 'is_active':
            product.is_active = value == 'true'
            product.save()
            return JsonResponse({'success': True, 'value': product.is_active})

    from django.http import JsonResponse
    return JsonResponse({'error': 'Invalid request'}, status=400)
