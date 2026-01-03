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


class OrderSpecialMealIngredientInline(admin.StackedInline):
    model = OrderSpecialMealIngredient
    extra = 0
    

from django.utils.html import format_html, format_html_join


class OrderSpecialMealInline(admin.StackedInline):
    model = OrderSpecialMeal
    extra = 0
    readonly_fields = ['total_price', 'show_ingredients']
    fields = ('special_meal', 'quantity', 'total_price', 'show_ingredients')
    show_change_link = True

    def show_ingredients(self, obj):
        if not obj.pk:
            return "-"

        ingredients = obj.selected_ingredients.all()

        if not ingredients.exists():
            return "— No ingredients —"

        return format_html(
            "<div style='margin-top:8px;padding:8px;border:1px solid #ddd;"
            "border-radius:8px;'>"
            "<strong>Ingredients:</strong><br><ul style='margin-top:6px'>{}</ul>"
            "</div>",
            format_html_join(
                "",
                "<li>{} (x{}) — {} DA</li>",
                [
                    (
                        ing.ingredient.name,
                        ing.quantity,
                        ing.unit_price
                    )
                    for ing in ingredients
                ]
            )
        )

    show_ingredients.short_description = "Selected Ingredients"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_phone',
        'customer_name',
        'customer_address',
        'order_summary',   
        'additional_notes',
        'total_price',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['customer_phone', 'customer_name', 'id']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    inlines = [OrderItemInline, OrderSpecialMealInline]


    def order_summary(self, obj):
        # Regular products
        item_lines = [
            f"{i.quantity}x {i.product.name}"
            for i in obj.items.all()
        ]

        # Special meals with ingredients
        special_lines = []
        for sm in obj.special_meals.all():

            ingredients = ", ".join(
                f"{ing.quantity}x {ing.ingredient.name}"
                for ing in sm.selected_ingredients.all()
            )

            if ingredients:
                special_lines.append(
                    f"{sm.quantity}x {sm.special_meal.name} "
                    f"[{ingredients}]"
                )
            else:
                special_lines.append(
                    f"{sm.quantity}x {sm.special_meal.name}"
                )

        lines = item_lines + special_lines

        if not lines:
            return "—"

        return format_html_join(
            format_html("<br>"),
            "{}",
            ((line,) for line in lines)
        )

    order_summary.allow_tags = True
    order_summary.short_description = "Order Items"

    class Media:
        js = ("admin/order_auto_refresh.js",)

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