from django.contrib import admin
from .models import (
    Category, Product, IngredientCategory, Ingredient, 
    SpecialMeal, SpecialMealIngredient, Order, OrderItem,
    OrderSpecialMeal, OrderSpecialMealIngredient,
    Cart, CartItem, CartSpecialMeal, CartSpecialMealIngredient
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_featured']
    list_filter = ['category', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_featured']


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name']
    list_editable = ['price', 'is_available']


class SpecialMealIngredientInline(admin.TabularInline):
    model = SpecialMealIngredient
    extra = 1


@admin.register(SpecialMeal)
class SpecialMealAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'is_available']
    list_filter = ['is_available']
    search_fields = ['name', 'description']
    inlines = [SpecialMealIngredientInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


class OrderSpecialMealIngredientInline(admin.TabularInline):
    model = OrderSpecialMealIngredient
    extra = 0


class OrderSpecialMealInline(admin.StackedInline):
    model = OrderSpecialMeal
    extra = 0
    readonly_fields = ['total_price']
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_phone', 'customer_name', 
        'total_price', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['customer_phone', 'customer_name', 'id']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    inlines = [OrderItemInline, OrderSpecialMealInline]
    
    fieldsets = (
        ('Informations Client', {
            'fields': ('customer_phone', 'customer_name', 'customer_address')
        }),
        ('Détails de la Commande', {
            'fields': ('total_price', 'status', 'additional_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderSpecialMeal)
class OrderSpecialMealAdmin(admin.ModelAdmin):
    list_display = ['order', 'special_meal', 'quantity', 'total_price']
    inlines = [OrderSpecialMealIngredientInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartSpecialMealInline(admin.TabularInline):
    model = CartSpecialMeal
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at', 'get_total']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline, CartSpecialMealInline]