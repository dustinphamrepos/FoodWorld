from django.shortcuts import get_object_or_404, render
from django.db.models import Prefetch

from menu.models import Category, FoodItem
from vendor.models import Vendor

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
  context = {
    'vendor': vendor,
    'categories': categories
  }
  return render(request, 'marketplace/vendor_detail.html', context)

def vendor_detail_by_category(request, vendor_slug, pk):
  vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
  categories = Category.objects.filter(vendor=vendor).prefetch_related(
    Prefetch(
      'food_items_by_category',
      queryset=FoodItem.objects.filter(is_available=True)
    )
  )
  category = Category.objects.get(pk=pk)
  food_items = FoodItem.objects.filter(category__id=pk)
  context = {
    'vendor': vendor,
    'categories': categories,
    'category': category,
    'food_items': food_items,
    'pk': pk,
  }
  return render(request, 'marketplace/vendor_detail_by_category.html', context)