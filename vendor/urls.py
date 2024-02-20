from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
  path('', AccountViews.vendorDashboard, name='vendor'),
  path('profile/', views.vendor_profile, name='vendor_profile'),
  path('menu-builder/', views.menu_builder, name='menu_builder'),
  path('menu-builder/category/<int:pk>/', views.food_items_by_category, name='food_items_by_category'),

  # Category CRUD
  path('menu-builder/category/add/', views.add_category, name='add_category'),
  path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit_category'),
  path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete_category'),
  
  # Food Item CRUD
  path('menu-builder/food_item/add/', views.add_food_item, name='add_food_item'),
  path('menu-builder/food_item/add_with_category/<int:pk>', views.add_food_item_with_category, name='add_food_item_with_category'),
  path('menu-builder/food_item/edit/<int:pk>', views.edit_food_item, name='edit_food_item'),
  path('menu-builder/food_item/delete/<int:pk>', views.delete_food_item, name='delete_food_item'),

]