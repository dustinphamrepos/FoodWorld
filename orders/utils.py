import datetime
from decimal import Decimal
import json

def generate_order_number(pk):
  current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
  order_number = current_datetime + str(pk)
  return order_number

def order_total_by_vendor(order, vendor):
    total_data = json.loads(order.total_data) #{"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}
    data = total_data.get(str(vendor.id)) #{'67.00': "{'VAT': {'5.00': '3.35'}, 'TAV': {'8.00': '5.36'}}"}
    subtotal = 0
    tax = 0
    tax_dict = {}
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