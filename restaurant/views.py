from django.shortcuts import render


from django.shortcuts import render
from .models import Category, Product

def menu(request):
    # Get all categories with their products
    categories = Category.objects.prefetch_related('product_set').all()
    
    # Get featured/popular products (you can customize this logic)
    featured_products = Product.objects.filter(is_available=True)[:4]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'menu/menu.html', context)