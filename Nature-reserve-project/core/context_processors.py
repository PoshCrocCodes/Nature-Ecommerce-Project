from products.models import Category


def site_info(request):
    """Provide global site info to all templates."""
    categories = Category.objects.filter(is_active=True).order_by('order')[:8]
    return {
        'nav_categories': categories,
        'site_name': 'Greenfield Local Hub',
    }
