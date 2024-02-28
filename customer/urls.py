from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.customerDashboard, name='customer'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.customer_my_orders, name='customer_my_orders'),
    path('customer-order-detail/<int:order_number>/', views.customer_order_detail, name='customer_order_detail'),
]
