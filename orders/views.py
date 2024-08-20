from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, HttpResponse
import simplejson as json
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
import uuid
import hmac
import hashlib
from django.utils.encoding import force_bytes
import requests

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from .forms import OrderForm
from .models import Order, OrderedFood, Payment
from .utils import generate_order_number, order_total_by_vendor
from accounts.utils import send_notification

# Create your views here.
@login_required(login_url='login')
def place_order(request):
  cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect('marketplace')
  
  vendors_ids = []
  for cart_item in cart_items:
    if cart_item.food_item.vendor.id not in vendors_ids:
      vendors_ids.append(cart_item.food_item.vendor.id)
  # print(vendors_ids)
  
  get_tax = Tax.objects.filter(is_active=True)
  subtotal = 0
  total_data = {} # {"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}
  k = {}
  for cart_item in cart_items:
    food_item = cart_item.food_item
    vendor_id = food_item.vendor.id
    if vendor_id in k:
      subtotal = k[vendor_id]
      subtotal += food_item.price * cart_item.quantity
      k[vendor_id] = subtotal
    else:
      subtotal = food_item.price * cart_item.quantity
      k[vendor_id] = subtotal
  # print(food_item, food_item.vendor.id)
    # print(subtotal) {"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}
  # print(k)
    # Calculate the tax_data
    tax_dict = {}
    for tax_item in get_tax:
      tax_type = tax_item.tax_type
      tax_percentage = tax_item.tax_percentage
      tax_amount = round((tax_percentage * subtotal)/100, 2)
      tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
    # print(tax_dict)
    
    # Construct total_data
    total_data.update({food_item.vendor.id: {str(subtotal): str(tax_dict)}})
  #print(total_data)
    
  # subtotal = get_cart_amounts(request)['subtotal']
  total_tax = get_cart_amounts(request)['tax']
  tax_data = get_cart_amounts(request)['tax_dict']
  grand_total = get_cart_amounts(request)['grand_total']
  # print(subtotal, grand_total, tax_data, total_tax)
  if request.method == 'POST':
    form = OrderForm(request.POST)
    if form.is_valid():
      order = Order()
      order.first_name = form.cleaned_data['first_name']
      order.last_name = form.cleaned_data['last_name']
      order.phone_number = form.cleaned_data['phone_number']
      order.email = form.cleaned_data['email']
      order.address = form.cleaned_data['address']
      order.country = form.cleaned_data['country']
      order.city = form.cleaned_data['city']
      order.district = form.cleaned_data['district']
      order.pin_code = form.cleaned_data['pin_code']

      order.user = request.user
      order.total = grand_total
      order.tax_data = json.dumps(tax_data)
      order.total_data = json.dumps(total_data)
      order.total_tax = total_tax
      order.payment_method = request.POST['payment-method']
      
      order.save()

      order.order_number = generate_order_number(order.id)
      order.vendors.add(*vendors_ids)
      order.save()

      context = {
        'order': order,
        'cart_items': cart_items,
      }
      
      return render(request, 'orders/place_order.html', context)
    else:
      print(form.errors)

  return render(request, 'orders/place_order.html',)

@login_required(login_url='login')
def payments(request):
  # Check if the request is ajax or not
  if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
    # Store the payment details in the payment model
    order_number = request.POST.get('order_number')
    transaction_id = request.POST.get('transaction_id')
    payment_method = request.POST.get('payment_method')
    status = request.POST.get('status')
    # print(order_number, transaction_id, payment_method, status)

    order = Order.objects.get(user=request.user, order_number=order_number)
    payment = Payment.objects.create(
      user = request.user,
      transaction_id = transaction_id,
      payment_method = payment_method,
      amount = order.total,
      status = status
    )

    # Update the order model
    order.payment = payment
    order.is_ordered = True
    order.save()
    # return HttpResponse("Saved!")

    # Move the cart items to order food model
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
      ordered_food = OrderedFood()
      ordered_food.order = order
      ordered_food.payment = payment
      ordered_food.user = request.user
      ordered_food.food_item = cart_item.food_item
      ordered_food.quantity = cart_item.quantity
      ordered_food.price = cart_item.food_item.price
      ordered_food.amount = cart_item.food_item.price * cart_item.quantity
      ordered_food.save()
    # return HttpResponse("Saved the ordered food.")
      
    # Send order confirmation to the customer
    mail_subject = 'Thank you for ordering with us!'
    mail_template = 'orders/order_confirmation_email.html'
    ordered_foods = OrderedFood.objects.filter(order=order)
    customer_subtotal = 0
    for ordered_food in ordered_foods:
      customer_subtotal += ordered_food.price * ordered_food.quantity
    tax_data = json.loads(order.tax_data)

    context = {
      'user': request.user,
      'order': order,
      'to_email': order.email,
      'ordered_foods': ordered_foods,
      'domain': get_current_site(request),
      'customer_subtotal': customer_subtotal,
      'tax_data': tax_data,
    }
    send_notification(mail_subject, mail_template, context)
    #return HttpResponse('Data saved and Email sent to customer.')

    # Send order received email to the vendor
    mail_subject = 'You have received a new order.'
    mail_template = 'orders/new_order_received.html'
    to_emails = []
    for cart_item in cart_items:
      if cart_item.food_item.vendor.user.email not in to_emails:
        to_emails.append(cart_item.food_item.vendor.user.email)
        ordered_food_to_vendor = OrderedFood.objects.filter(order=order, food_item__vendor=cart_item.food_item.vendor)
        # print(ordered_food_to_vendor)
    # print(to_emails)
        context = {
          'order': order,
          'to_email': cart_item.food_item.vendor.user.email,
          'ordered_food_to_vendor': ordered_food_to_vendor,
          'vendor_subtotal': order_total_by_vendor(order, cart_item.food_item.vendor)['subtotal'],
          'vendor_tax_data': order_total_by_vendor(order, cart_item.food_item.vendor)['tax_dict'],
          'vendor_grand_total': order_total_by_vendor(order, cart_item.food_item.vendor)['grand_total'],
        }
        send_notification(mail_subject, mail_template, context)
    # return HttpResponse('Data saved and Email sent to vendor.')

    # Clear the cart if the payment is success
    cart_items.delete()
    # return HttpResponse('Deleted.')

    # Return back to ajax with the status success or failure
    response = {
      'order_number': order_number,
      'transaction_id': transaction_id,
    }
    return JsonResponse(response)

  return HttpResponse("Payments view")

@login_required(login_url='login')
def payments_by_momo(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Lấy thông tin thanh toán từ request
        order_number = request.POST.get('order_number')
        order = Order.objects.get(user=request.user, order_number=order_number)
        transaction_id = str(uuid.uuid4())
        payment_method = 'Momo'
        status = 'success'
        orderId = force_bytes(str(uuid.uuid4()))
        #orderId = order.id

        # Các thông tin cần cho thanh toán Momo
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        partnerCode = force_bytes("MOMO")
        accessKey = force_bytes("F8BBA842ECF85")
        secretKey = force_bytes("K951B6PE1waDMi640xX08PD3vg6EkVlz")
        orderInfo = force_bytes(f"Thanh toán đơn hàng {order_number}")
        redirectUrl = force_bytes("http://127.0.0.1:8000/")
        ipnUrl = force_bytes("http://127.0.0.1:8000/")
        amount = force_bytes(str(order.total))  # Chuyển amount thành bytes
        requestId = force_bytes(str(uuid.uuid4()))
        requestType = force_bytes("captureWallet")
        extraData = force_bytes("")

        # Tạo chuỗi rawSignature để tạo chữ ký
        rawSignature = force_bytes(f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}")

        # Tạo chữ ký từ rawSignature
        h = hmac.new(secretKey, rawSignature, hashlib.sha256)
        signature = h.hexdigest()

        # Tạo dữ liệu JSON để gửi đến endpoint của Momo
        data = {
            'partnerCode': partnerCode,
            'partnerName': "Test",
            'storeId': "MomoTestStore",
            'requestId': requestId,
            'amount': amount,
            'orderId': orderId,
            'orderInfo': orderInfo,
            'redirectUrl': redirectUrl,
            'ipnUrl': ipnUrl,
            'lang': "vi",
            'extraData': extraData,
            'requestType': requestType,
            'signature': signature
        }
        print("dt:", data)

        # Gửi yêu cầu thanh toán đến Momo endpoint
        response = requests.post(endpoint, json=data)
        # Sau khi thực hiện yêu cầu đến API MoMo
        print(response.text)


        # Lấy payUrl từ phản hồi của Momo
        payUrl = response.json().get('payUrl', None)

        if payUrl:
            # Bạn có thể lưu thông tin thanh toán và cập nhật trạng thái đơn hàng tại đây
            payment = Payment.objects.create(
                user=request.user,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=order.total,
                status=status
            )

            # Cập nhật trạng thái đơn hàng
            order.payment = payment
            order.is_ordered = True
            order.save()

            # Chuyển hướng người dùng đến trang thanh toán Momo
            return JsonResponse({'redirect_url': payUrl})
        else:
            return JsonResponse({'error': 'Failed to get payUrl from Momo'})

    return JsonResponse({'error': 'Invalid request'})


def order_complete(request):
  order_number = request.GET.get('order_no')
  transaction_id = request.GET.get('trans_id')

  try:
    order = Order.objects.get(order_number=order_number,
                              payment__transaction_id=transaction_id,
                              is_ordered=True)
    ordered_foods = OrderedFood.objects.filter(order=order)
    subtotal = 0
    for ordered_food_item in ordered_foods:
      subtotal += ordered_food_item.price * ordered_food_item.quantity

    tax_data = json.loads(order.tax_data)

    context = {
      'order': order,
      'ordered_foods': ordered_foods,
      'subtotal': subtotal,
      'tax_data': tax_data,
    }
    return render(request, 'orders/order_complete.html', context)
  except:
    return redirect('home')