from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import UserProfile

from orders.forms import OrderForm
from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import OpeningHour, Vendor
from .context_processors import get_cart_counter, get_cart_amounts

# Create your views here.
def marketplace(request):
  vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count
  }
  return render(request, 'marketplace/vendors_list.html', context)

def vendor_detail(request, vendor_slug):
  vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
  categories = Category.objects.filter(vendor=vendor).prefetch_related(
    Prefetch(
      'food_items_by_category',
      queryset=FoodItem.objects.filter(is_available=True)
    )
  )
  
  list_food_item_id = []
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
      food_item_id = cart_item.food_item.id
      list_food_item_id.append(food_item_id)
  else:
    cart_items = None
  
  opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')
  
  # Check current day's opening hours
  today_date = date.today()
  today = today_date.isoweekday()
  current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

  context = {
    'vendor': vendor,
    'categories': categories,
    'cart_items': cart_items,
    'list_food_item_id': list_food_item_id,
    'opening_hours': opening_hours,
    'current_opening_hours': current_opening_hours,
  }
  return render(request, 'marketplace/vendor_detail.html', context)

def vendor_detail_by_category(request, vendor_slug, category_id):
  vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
  categories = Category.objects.filter(vendor=vendor).prefetch_related(
    Prefetch(
      'food_items_by_category',
      queryset=FoodItem.objects.filter(is_available=True)
    )
  )
  category = Category.objects.get(id=category_id)
  food_items = FoodItem.objects.filter(category__id=category_id)

  list_food_item = []
  for food_item in food_items:
    list_food_item.append(food_item)

  list_food_item_id = []
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(food_item__in=list_food_item)
    for cart_item in cart_items:
      food_item_id = cart_item.food_item.id
      list_food_item_id.append(food_item_id)
  else:
    cart_items = None
  
  opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')
  
  # Check current day's opening hours
  today_date = date.today()
  today = today_date.isoweekday()
  current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
  
  context = {
    'vendor': vendor,
    'categories': categories,
    'category': category,
    'food_items': food_items,
    'category_id': category_id,
    'cart_items': cart_items,
    'list_food_item_id': list_food_item_id,
    'opening_hours': opening_hours,
    'current_opening_hours': current_opening_hours,
  }
  return render(request, 'marketplace/vendor_detail_by_category.html', context)

@login_required(login_url='login')
def add_to_cart(request, food_item_id=None):
  if request.user.is_authenticated:
    if request.is_ajax():
      # Check if food item exists
      try:
        food_item = FoodItem.objects.get(id=food_item_id)
        # Check if the user already added that food item to the cart
        try:
          check_cart_by_food_item = Cart.objects.get(user=request.user, food_item=food_item)
          # Increase quantity of the food item
          check_cart_by_food_item.quantity += 1
          check_cart_by_food_item.save()
          return JsonResponse({
            'status': 'Success',
            'message': 'Increased quantity of the food item.',
            'cart_counter': get_cart_counter(request),
            'cart_amounts': get_cart_amounts(request),
            'quantity_by_cart_item': check_cart_by_food_item.quantity,
          })
        except Cart.DoesNotExist:
          check_cart_by_food_item = Cart.objects.create(user=request.user, food_item=food_item, quantity=1)
          return JsonResponse({
            'status': 'Success',
            'message': 'Added the food item to the cart.',
            'cart_counter': get_cart_counter(request),
            'cart_amounts': get_cart_amounts(request),
            'quantity_by_cart_item': check_cart_by_food_item.quantity
          })
      except FoodItem.DoesNotExist:
        return JsonResponse({'status': 'Failed', 'message': 'This food does not exist.'})
    else:
      return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
  else:
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue!'})

@login_required(login_url='login') 
def decrease_cart(request, food_item_id):
  if request.user.is_authenticated:
    if request.is_ajax():
      # Check if food item exists
      try:
        food_item = FoodItem.objects.get(id=food_item_id)
        # Check if the user already added that food item to the cart
        try:
          check_cart_by_food_item = Cart.objects.get(user=request.user, food_item=food_item)
          
          cart_item_id = check_cart_by_food_item.id
          if check_cart_by_food_item.quantity > 1:
            # Decrease quantity of the food item
            check_cart_by_food_item.quantity -= 1
            check_cart_by_food_item.save()
          else:
            check_cart_by_food_item.delete()
            check_cart_by_food_item.quantity = 0
          return JsonResponse({
            'status': 'Success',
            'message': 'Decreased quantity of the food item.',
            'cart_counter': get_cart_counter(request),
            'cart_amounts': get_cart_amounts(request),
            'quantity': check_cart_by_food_item.quantity,
            'cart_item_id': cart_item_id
          })
        except Cart.DoesNotExist:
          return JsonResponse({
            'status': 'Failed',
            'message': 'You do not have this food item in your cart.'
          })
      except FoodItem.DoesNotExist:
        return JsonResponse({'status': 'Failed', 'message': 'This food does not exist.'})
    else:
      return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})
  else:
    return JsonResponse({'status': 'login_required', 'message': 'Please login to continue!'})

@login_required(login_url='login')  
def cart(request):
  cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
  context = {
    'cart_items': cart_items,
  }
  return render(request, 'marketplace/cart.html', context)

@login_required(login_url='login')
def delete_cart(request, cart_item_id):
  if request.user.is_authenticated:
    if request.is_ajax():
      try:
        # Check if cart item exists
        cart_item = Cart.objects.get(user=request.user, id=cart_item_id)
        if cart_item:
          cart_item.delete()
          return JsonResponse({
            'status': 'Success',
            'message': 'Cart item has been deleted.',
            'cart_counter': get_cart_counter(request),
            'cart_amounts': get_cart_amounts(request),
          })
      except:
        return JsonResponse({'status': 'Failed', 'message': 'This cart item does not exist.'})
    else:
      return JsonResponse({'status': 'Failed', 'message': 'Invalid request.'})

def search(request):
  address = request.GET['address']
  latitude = request.GET['lat']
  longitude = request.GET['lng']
  radius = request.GET['radius']
  keyword = request.GET['keyword']

  # Get vendor ids that has fooItem the user is looking for
  fetch_vendors_by_food_items = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
  vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_food_items) | 
                                  Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
  vendor_count = vendors.count()
  context = {
    'vendors': vendors,
    'vendor_count': vendor_count,
  }
  return render(request, 'marketplace/vendors_list.html', context)

@login_required(login_url='login')
def checkout(request):
  cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect('marketplace')
  user_profile = UserProfile.objects.get(user=request.user)
  default_values = {
    'first_name': request.user.first_name,
    'last_name': request.user.last_name,
    'phone_number': request.user.phone_number,
    'email': request.user.email,
    'address': user_profile.address,
    'country': user_profile.country,
    'city': user_profile.city,
    'district': user_profile.district,
    'pin_code': user_profile.pin_code
  }
  form = OrderForm(initial=default_values)

  context = {
    'form': form,
    'cart_items': cart_items,
  }
  return render(request, 'marketplace/checkout.html', context)