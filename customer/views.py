import simplejson as json
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from orders.models import Order, OrderedFood

# Create your views here.
@login_required(login_url='login')
def customer_profile(request):
  profile = get_object_or_404(UserProfile, user=request.user)
  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    user_form = UserInfoForm(request.POST, instance=request.user)
    if profile_form.is_valid() and user_form.is_valid():
      profile_form.save()
      user_form.save()
      messages.success(request, 'User profile updated successfully.')
      return redirect('customer_profile')
    else:
      print(profile_form.errors)
      print(user_form.errors)
  else:
    profile_form = UserProfileForm(instance=profile)
    user_form = UserInfoForm(instance=request.user)

  context = {
    'profile': profile,
    'profile_form': profile_form,
    'user_form': user_form,
  }
  return render(request, 'customer/customer_profile.html', context)

def customer_my_orders(request):
  orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('created_at')

  context = {
    'orders': orders,
  }
  return render(request, 'customer/customer_my_orders.html', context)

def customer_order_detail(request, order_number):
  try:
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_foods = OrderedFood.objects.filter(order=order)
    # print(ordered_food)
    subtotal = 0
    for ordered_food in ordered_foods:
      subtotal += ordered_food.price * ordered_food.quantity
    tax_data = json.loads(order.tax_data)
    context = {
      'order': order,
      'ordered_foods': ordered_foods,
      'subtotal': subtotal,
      'tax_data': tax_data,
    }
    return render(request, 'customer/customer_order_detail.html', context)
  except:
    return redirect('customer')