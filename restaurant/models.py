from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Existing Models
class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# New Models for Special Meals and Ingredients
class IngredientCategory(models.Model):
    """Categories for ingredients (Pain, Viandes, Légumes, Sauces, etc.)"""
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0, help_text="Order of display")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Ingredient Categories"


class Ingredient(models.Model):
    """Individual ingredients for customizing meals"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(IngredientCategory, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        help_text="Extra cost for this ingredient (0 if included in base)"
    )
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='ingredients/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    class Meta:
        ordering = ['category__order', 'name']


class SpecialMeal(models.Model):
    """Special customizable meals like sandwiches"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='special_meals/')
    is_available = models.BooleanField(default=True)
    
    # Available ingredients for this special meal
    available_ingredients = models.ManyToManyField(
        Ingredient,
        through='SpecialMealIngredient',
        related_name='special_meals'
    )

    def __str__(self):
        return self.name


class SpecialMealIngredient(models.Model):
    """Through model to manage which ingredients are available for each special meal"""
    special_meal = models.ForeignKey(SpecialMeal, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    is_default = models.BooleanField(
        default=False,
        help_text="Is this ingredient included by default?"
    )
    max_quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum quantity allowed for this ingredient"
    )

    class Meta:
        unique_together = ['special_meal', 'ingredient']

    def __str__(self):
        return f"{self.special_meal.name} - {self.ingredient.name}"


# Order and Cart Models
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    # Customer Information
    customer_phone = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_address = models.TextField(blank=True, null=True)
    
    # Order Details
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.customer_phone} - {self.total_price} DA"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Regular products in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class OrderSpecialMeal(models.Model):
    """Customized special meals in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='special_meals')
    special_meal = models.ForeignKey(SpecialMeal, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity}x {self.special_meal.name} (Personnalisé)"


class OrderSpecialMealIngredient(models.Model):
    """Selected ingredients for a special meal in an order"""
    order_special_meal = models.ForeignKey(
        OrderSpecialMeal, 
        on_delete=models.CASCADE, 
        related_name='selected_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.ingredient.name}"


# Session-based Cart (optional - for temporary storage before order)
class Cart(models.Model):
    """Cart tied to session or user"""
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        total = Decimal('0.00')
        for item in self.cart_items.all():
            total += item.total_price
        for special in self.cart_special_meals.all():
            total += special.total_price
        return total

    def __str__(self):
        return f"Panier {self.session_key}"


class CartItem(models.Model):
    """Regular products in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class CartSpecialMeal(models.Model):
    """Customized special meals in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_special_meals')
    special_meal = models.ForeignKey(SpecialMeal, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def calculate_total(self):
        """Calculate total including ingredients"""
        total = self.special_meal.base_price * self.quantity
        for ing in self.selected_ingredients.all():
            total += ing.ingredient.price * ing.quantity * self.quantity
        self.total_price = total
        return total

    def __str__(self):
        return f"{self.quantity}x {self.special_meal.name}"


class CartSpecialMealIngredient(models.Model):
    """Selected ingredients for special meal in cart"""
    cart_special_meal = models.ForeignKey(
        CartSpecialMeal,
        on_delete=models.CASCADE,
        related_name='selected_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity}x {self.ingredient.name}"