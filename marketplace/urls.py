from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('restaurants/<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('restaurants/<slug:vendor_slug>/<int:category_id>/', views.vendor_detail_by_category, name='vendor_detail_by_category'),
    
    # Add to cart
    path('add-to-cart/<int:food_item_id>/', views.add_to_cart, name='add_to_cart'),
    # Decrease cart
    path('decrease-cart/<int:food_item_id>/', views.decrease_cart, name='decrease_cart'),
    # Delete cart item
    path('delete-cart/<int:cart_item_id>/', views.delete_cart, name='delete_cart'),
    
]
