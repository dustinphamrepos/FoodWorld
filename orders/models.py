from decimal import Decimal
import simplejson as json
from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor

# Create your models here.
request_object = ''

class Payment(models.Model):
  PAYMENT_METHOD = (
    ('PayPal', 'PayPal'),
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  transaction_id = models.CharField(max_length=100)
  payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
  amount = models.CharField(max_length=10)
  status = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.transaction_id

class Order(models.Model):
  STATUS = (
    ('New', 'New'),
    ('Accepted', 'Accepted'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
  )

  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  vendors = models.ManyToManyField(Vendor, blank=True)
  order_number = models.CharField(max_length=20)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  phone_number = models.CharField(max_length=15, blank=True)
  email = models.EmailField(max_length=50)
  address = models.CharField(max_length=200)
  country = models.CharField(max_length=15, blank=True)
  city = models.CharField(max_length=50)
  district = models.CharField(max_length=50)
  pin_code = models.CharField(max_length=10)
  total = models.FloatField()
  tax_data = models.JSONField(blank=True, help_text = "Data format: {'tax_type':{'tax_percentage':'tax_amount'}}", null=True)
  total_data = models.JSONField(blank=True, null=True)
  total_tax = models.FloatField()
  payment_method = models.CharField(max_length=25)
  status = models.CharField(max_length=15, choices=STATUS, default='New')
  is_ordered = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  @property
  def name(self):
    return f'{self.first_name} {self.last_name}'
  
  def created_at_date(self):
    if self.created_at:
      return self.created_at.date()
    return None
  
  def order_placed_to(self):
    if self.vendors.count() == 1:
      return str(self.vendors.first())
    elif self.vendors.count() > 1:
      return ", ".join([str(vendor) for vendor in self.vendors.all()])
    else:
      return "No vendor specified"
    
  def get_total_by_vendor(self):
    vendor = Vendor.objects.get(user=request_object.user)
    # print(vendor)
    subtotal = 0
    tax = 0
    tax_dict = {}
    if self.total_data:
      total_data = json.loads(self.total_data) # {"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}
      data = total_data.get(str(vendor.id))
      # print(data) {'67.00': "{'VAT': {'5.00': '3.35'}, 'TAV': {'8.00': '5.36'}}"}
      if data:
        for key, val in data.items():
          subtotal += float(key)
          val = val.replace("'", '"')
          val = json.loads(val)
          tax_dict.update(val)
          # print(val) {'VAT': {'5.00': '3.35'}, 'TAV': {'8.00': '5.36'}}

          # Calculate tax
          for i in val:
            # print(val[i]) {'5.00': '3.35'}
            for j in val[i]:
              # print(val[i][j]) '3.35'
              tax += float(val[i][j])
    grand_total = Decimal(subtotal) + Decimal(tax)

    context = {
      'subtotal': subtotal,
      'tax_dict': tax_dict,
      'grand_total': grand_total.quantize(Decimal('0.00')),
    }
    return context


  def __str__(self):
    return self.order_number

class OrderedFood(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
  quantity = models.IntegerField()
  price = models.FloatField()
  amount = models.FloatField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.food_item.food_title