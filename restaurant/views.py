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



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
import json

from .models import (
    Category, Product, SpecialMeal, Ingredient, IngredientCategory,
    Cart, CartItem, CartSpecialMeal, CartSpecialMealIngredient,
    Order, OrderItem, OrderSpecialMeal, OrderSpecialMealIngredient
)


def get_or_create_cart(request):
    """Get or create cart for current session"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def order_page(request):
    """Main order page showing special meals and categories"""
    special_meals = SpecialMeal.objects.filter(is_available=True)
    categories = Category.objects.prefetch_related('product_set').all()
    cart = get_or_create_cart(request)
    
    context = {
        'special_meals': special_meals,
        'categories': categories,
        'cart': cart,
        'cart_total': cart.get_total(),
        'cart_items_count': cart.cart_items.count() + cart.cart_special_meals.count()
    }
    return render(request, 'restaurant/order.html', context)


def customize_special_meal(request, meal_id):
    """Page to customize a special meal with ingredients"""
    special_meal = get_object_or_404(SpecialMeal, id=meal_id, is_available=True)
    
    # Get available ingredients grouped by category
    ingredient_categories = IngredientCategory.objects.prefetch_related(
        'ingredient_set'
    ).all()
    
    # Get which ingredients are available for this meal
    available_ingredient_ids = special_meal.specialmealingredient_set.values_list(
        'ingredient_id', flat=True
    )
    
    # Get default ingredients
    default_ingredients = special_meal.specialmealingredient_set.filter(
        is_default=True
    ).select_related('ingredient')
    
    context = {
        'special_meal': special_meal,
        'ingredient_categories': ingredient_categories,
        'available_ingredient_ids': list(available_ingredient_ids),
        'default_ingredients': default_ingredients,
    }
    return render(request, 'restaurant/customize_meal.html', context)


@require_POST
def add_to_cart(request):
    """Add regular product to cart"""
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        cart = get_or_create_cart(request)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} ajouté au panier',
            'cart_total': float(cart.get_total()),
            'cart_count': cart.cart_items.count() + cart.cart_special_meals.count()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def add_special_meal_to_cart(request):
    """Add customized special meal to cart"""
    try:
        data = json.loads(request.body)
        meal_id = data.get('meal_id')
        quantity = int(data.get('quantity', 1))
        ingredients = data.get('ingredients', [])  # List of {id, quantity}
        notes = data.get('notes', '')
        
        special_meal = get_object_or_404(SpecialMeal, id=meal_id, is_available=True)
        cart = get_or_create_cart(request)
        
        # Create cart special meal
        cart_special = CartSpecialMeal.objects.create(
            cart=cart,
            special_meal=special_meal,
            quantity=quantity,
            notes=notes,
            total_price=special_meal.base_price * quantity
        )
        
        # Add ingredients
        total_ingredients_price = Decimal('0.00')
        for ing_data in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ing_data['id'])
            ing_quantity = int(ing_data.get('quantity', 1))
            
            CartSpecialMealIngredient.objects.create(
                cart_special_meal=cart_special,
                ingredient=ingredient,
                quantity=ing_quantity
            )
            total_ingredients_price += ingredient.price * ing_quantity
        
        # Update total price
        cart_special.total_price = (special_meal.base_price + total_ingredients_price) * quantity
        cart_special.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{special_meal.name} personnalisé ajouté au panier',
            'cart_total': float(cart.get_total()),
            'cart_count': cart.cart_items.count() + cart.cart_special_meals.count()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def view_cart(request):
    """View cart contents"""
    cart = get_or_create_cart(request)
    
    # Get all cart items with details
    cart_items = cart.cart_items.select_related('product').all()
    cart_special_meals = cart.cart_special_meals.select_related('special_meal').prefetch_related(
        'selected_ingredients__ingredient'
    ).all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_special_meals': cart_special_meals,
        'cart_total': cart.get_total()
    }
    return render(request, 'restaurant/cart.html', context)


@require_POST
def update_cart_item(request):
    """Update quantity of cart item"""
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))
        item_type = request.POST.get('type')  # 'product' or 'special'
        
        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Quantité invalide'}, status=400)
        
        cart = get_or_create_cart(request)
        
        if item_type == 'product':
            item = get_object_or_404(CartItem, id=item_id, cart=cart)
            item.quantity = quantity
            item.save()
        else:
            item = get_object_or_404(CartSpecialMeal, id=item_id, cart=cart)
            item.quantity = quantity
            item.calculate_total()
            item.save()
        
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total())
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    try:
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('type')
        
        cart = get_or_create_cart(request)
        
        if item_type == 'product':
            CartItem.objects.filter(id=item_id, cart=cart).delete()
        else:
            CartSpecialMeal.objects.filter(id=item_id, cart=cart).delete()
        
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total()),
            'cart_count': cart.cart_items.count() + cart.cart_special_meals.count()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def checkout(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    
    if not cart.cart_items.exists() and not cart.cart_special_meals.exists():
        messages.warning(request, 'Votre panier est vide')
        return redirect('restaurant:order')
    
    context = {
        'cart': cart,
        'cart_total': cart.get_total()
    }
    return render(request, 'restaurant/checkout.html', context)


@require_POST
def place_order(request):
    """Create order from cart"""
    try:
        cart = get_or_create_cart(request)
        
        if not cart.cart_items.exists() and not cart.cart_special_meals.exists():
            return JsonResponse({'success': False, 'message': 'Panier vide'}, status=400)
        
        # Get customer info
        customer_phone = request.POST.get('phone')
        customer_name = request.POST.get('name', '')
        customer_address = request.POST.get('address', '')
        additional_notes = request.POST.get('notes', '')
        
        if not customer_phone:
            return JsonResponse({'success': False, 'message': 'Numéro de téléphone requis'}, status=400)
        
        # Create order
        order = Order.objects.create(
            customer_phone=customer_phone,
            customer_name=customer_name,
            customer_address=customer_address,
            total_price=cart.get_total(),
            additional_notes=additional_notes
        )
        
        # Add regular items
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price
            )
        
        # Add special meals
        for cart_special in cart.cart_special_meals.all():
            order_special = OrderSpecialMeal.objects.create(
                order=order,
                special_meal=cart_special.special_meal,
                quantity=cart_special.quantity,
                base_price=cart_special.special_meal.base_price,
                total_price=cart_special.total_price,
                notes=cart_special.notes
            )
            
            # Add ingredients
            for ing in cart_special.selected_ingredients.all():
                OrderSpecialMealIngredient.objects.create(
                    order_special_meal=order_special,
                    ingredient=ing.ingredient,
                    quantity=ing.quantity,
                    unit_price=ing.ingredient.price
                )
        
        # Clear cart
        cart.cart_items.all().delete()
        cart.cart_special_meals.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Commande passée avec succès',
            'order_id': order.id
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order
    }
    return render(request, 'restaurant/order_confirmation.html', context)