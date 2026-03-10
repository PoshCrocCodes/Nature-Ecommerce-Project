from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm


def product_list(request):
    """Product listing with search and filter functionality."""
    products = Product.objects.filter(is_active=True).select_related('category', 'producer__profile')
    categories = Category.objects.filter(is_active=True)

    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(producer__profile__farm_name__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category', '')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Organic filter
    organic = request.GET.get('organic', '')
    if organic == 'true':
        products = products.filter(is_organic=True)

    # In stock filter
    in_stock = request.GET.get('in_stock', '')
    if in_stock == 'true':
        products = products.filter(stock__gt=0)

    # Sort
    sort = request.GET.get('sort', 'newest')
    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        'rating': '-created_at',  # Will annotate properly
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    # Annotate with average rating
    products = products.annotate(avg_rating=Avg('reviews__rating'))

    if sort == 'rating':
        products = products.order_by('-avg_rating')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'organic': organic,
        'in_stock': in_stock,
        'total_count': paginator.count,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Individual product detail page with reviews."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    user_review = None
    review_form = None

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        if not user_review:
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Thank you for your review!')
                    return redirect('product_detail', slug=slug)
            else:
                review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'user_review': user_review,
        'review_form': review_form,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """Producers can add new products."""
    if not request.user.profile.is_producer():
        messages.error(request, 'Only producers can add products.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.producer = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('producer_dashboard')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def edit_product(request, slug):
    """Producers edit their own products."""
    product = get_object_or_404(Product, slug=slug, producer=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('producer_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def delete_product(request, slug):
    """Producers delete their own products."""
    product = get_object_or_404(Product, slug=slug, producer=request.user)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('producer_dashboard')
    return render(request, 'products/product_confirm_delete.html', {'product': product})


def context_processors(request):
    """Provide cart count to all templates."""
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    return {'cart_count': cart_count}
