from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm, FoodItemWithCategoryForm
from menu.models import Category, FoodItem
from .forms import VendorForm
from .models import Vendor

# Create your views here.
def get_vendor(request):
  vendor = Vendor.objects.get(user=request.user)
  return vendor

def get_category(request, category_id=None):
  category = get_object_or_404(Category, id=category_id)
  return category

def get_food_item(request, food_item_id=None):
  food_item = get_object_or_404(FoodItem, id=food_item_id)
  return food_item

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_profile(request):
  profile = get_object_or_404(UserProfile, user=request.user)
  vendor = get_vendor(request)

  if request.method == 'POST':
    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
    vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

    if profile_form.is_valid() and vendor_form.is_valid():
      profile_form.save()
      vendor_form.save()
      messages.success(request, 'Settings updated.')
      return redirect('vendor_profile')
    else:
      print(profile_form.errors)
      print(vendor_form.errors)
  else:
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)

  context = {
    'profile_form': profile_form,
    'vendor_form': vendor_form,
    'profile': profile,
    'vendor': vendor
  }
  return render(request, 'vendor/vendor_profile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
  vendor = get_vendor(request)
  categories = Category.objects.filter(vendor=vendor)
  context = {
    'categories': categories,
  }
  return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def food_items_by_category(request, category_id=None):
  vendor = get_vendor(request)
  category = get_object_or_404(Category, id=category_id)
  food_items = FoodItem.objects.filter(vendor=vendor, category=category)
  print(food_items)
  context = {
    'food_items': food_items,
    'category': category,
  }
  return render(request, 'vendor/food_items_by_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.slug = slugify(category_name)
      form.save()
      messages.success(request, 'Category added successfully.')
      return redirect('menu_builder')
    else:
      print(form.errors)
  else:
    form = CategoryForm()
  context = {
      'form': form,
    }
  return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, category_id=None):
  category = get_category(request, category_id)
  if request.method == 'POST':
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
      category_name = form.cleaned_data['category_name']
      category = form.save(commit=False)
      category.vendor = get_vendor(request)
      category.slug = slugify(category_name)
      form.save()
      messages.success(request, 'Category updated successfully.')
      return redirect('menu_builder')
    else:
      print(form.errors)
  else:
    form = CategoryForm(instance=category)
  context = {
      'form': form,
      'category': category
    }
  return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, category_id=None):
  category = get_category(request, category_id)
  category.delete()
  messages.success(request, 'Category has been deleted successfully.')
  return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food_item(request):
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food_item = form.save(commit=False)
      food_item.vendor = get_vendor(request)
      food_item.slug = slugify(food_title)
      form.save()
      messages.success(request, 'Food Item added successfully.')
      return redirect('food_items_by_category', food_item.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm()
    # Modify form
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
  context = {
    'form': form,
  }
  return render(request, 'vendor/add_food_item.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food_item_with_category(request, category_id=None):
  category = get_category(request, category_id)
  if request.method == 'POST':
    form = FoodItemWithCategoryForm(request.POST, request.FILES)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food_item = form.save(commit=False)
      food_item.category = category
      food_item.vendor = get_vendor(request)
      food_item.slug = slugify(food_title)
      form.save()
      messages.success(request, 'Food Item added successfully.')
      return redirect('food_items_by_category', category_id)
    else:
      print(form.errors)
  else:
    form = FoodItemWithCategoryForm()
  context = {
    'form': form,
    'category': category
  }
  return render(request, 'vendor/add_food_item_with_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food_item(request, food_item_id=None):
  food_item = get_food_item(request, food_item_id)
  if request.method == 'POST':
    form = FoodItemForm(request.POST, request.FILES, instance=food_item)
    if form.is_valid():
      food_title = form.cleaned_data['food_title']
      food_item = form.save(commit=False)
      food_item.vendor = get_vendor(request)
      food_item.slug = slugify(food_title)
      form.save()
      messages.success(request, 'Food Item updated successfully.')
      return redirect('food_items_by_category', food_item.category.id)
    else:
      print(form.errors)
  else:
    form = FoodItemForm(instance=food_item)
    # Modify form
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
  context = {
      'form': form,
      'food_item': food_item
    }
  return render(request, 'vendor/edit_food_item.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food_item(request, food_item_id=None):
  food_item = get_food_item(request, food_item_id)
  food_item.delete()
  messages.success(request, 'Food Item has been deleted successfully.')
  return redirect('food_items_by_category', food_item.category.id)
