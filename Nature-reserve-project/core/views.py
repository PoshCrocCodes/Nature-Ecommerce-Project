from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product, Category, Review
from .models import CompanyInfo, FAQItem


def home(request):
    """Homepage with hero, shop-by categories, featured products, and top reviews."""
    categories = Category.objects.filter(is_active=True).order_by('order')[:8]
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True, stock__gt=0
    ).select_related('category')[:8]

    if featured_products.count() < 4:
        featured_products = Product.objects.filter(
            is_active=True, stock__gt=0
        ).select_related('category').order_by('-created_at')[:8]

    # Top reviews - highest rated, 4+ stars, approved, for homepage display
    top_reviews = Review.objects.filter(
        rating__gte=4,
        is_approved=True
    ).select_related('user', 'product').order_by('-rating', '-created_at')[:6]

    hero_info = CompanyInfo.objects.filter(section='about', is_active=True).first()

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'top_reviews': top_reviews,
        'hero_info': hero_info,
    }
    return render(request, 'home.html', context)


def about(request):
    """About page with company information sections."""
    sections = CompanyInfo.objects.filter(is_active=True).order_by('order')
    faqs = FAQItem.objects.filter(is_active=True)

    context = {
        'sections': sections,
        'faqs': faqs,
    }
    return render(request, 'core/about.html', context)


def cookie_policy(request):
    return render(request, 'core/cookie_policy.html')


def terms_and_conditions(request):
    return render(request, 'core/terms.html')


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


@require_POST
def set_cookie_consent(request):
    """Store cookie consent preference in session and set a cookie."""
    import json
    try:
        data = json.loads(request.body)
        consent = data.get('consent', 'essential')  # 'all', 'essential', or 'rejected'
    except (json.JSONDecodeError, KeyError):
        consent = 'essential'

    response = JsonResponse({'success': True, 'consent': consent})

    # Set a long-lived cookie recording consent
    response.set_cookie(
        'cookie_consent',
        consent,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=False,  # JS readable so we can check it client-side
        samesite='Lax',
    )

    # Record in session too
    request.session['cookie_consent'] = consent
    request.session.modified = True

    return response


def site_info_context(request):
    """Context processor helper."""
    return {}
