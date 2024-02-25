from menu.models import FoodItem
from .models import Cart, Tax

def get_cart_counter(request):
  cart_count = 0
  if request.user.is_authenticated:
    try:
      cart_items = Cart.objects.filter(user=request.user)
      if cart_items:
        for cart_item in cart_items:
          cart_count += cart_item.quantity
      else:
        cart_count = 0
    except:
      cart_count = 0
  return dict(cart_count=cart_count)

def get_cart_amounts(request):
  subtotal = 0
  tax = 0
  grand_total = 0
  tax_dict = {}
  if request.user.is_authenticated:
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
      food_item = FoodItem.objects.get(id=cart_item.food_item.id)
      subtotal += (food_item.price * cart_item.quantity)

    get_tax = Tax.objects.filter(is_active=True)
    # print(get_tax)
    for tax_item in get_tax:
      tax_type = tax_item.tax_type
      tax_percentage = tax_item.tax_percentage
      tax_amount = round((tax_percentage * subtotal)/100, 2)
      # print(tax_type, tax_percentage, tax_amount)
      tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})
      # print(tax_dict)
    tax = 0
    tax = sum(x for key in tax_dict.values() for x in key.values())
    # print(tax_dict)

    grand_total = subtotal + tax
  return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
      