from django.urls import path
from . import views

app_name='restaurant'

urlpatterns = [
    path("menu/",views.menu, name="menu"),
    # Order page
    path('commander/', views.order_page, name='order'),
    
    # Customize special meal
    path('personnaliser/<int:meal_id>/', views.customize_special_meal, name='customize_meal'),
    
    # Cart operations
    path('panier/', views.view_cart, name='cart'),
    path('ajouter-au-panier/', views.add_to_cart, name='add_to_cart'),
    path('ajouter-repas-special/', views.add_special_meal_to_cart, name='add_special_meal'),
    path('modifier-panier/', views.update_cart_item, name='update_cart'),
    path('retirer-du-panier/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('finaliser/', views.checkout, name='checkout'),
    path('passer-commande/', views.place_order, name='place_order'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

]
