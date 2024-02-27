from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.customerDashboard, name='customerDashboard'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.customer_my_orders, name='customer_my_orders'),
    path('order-detail/<int:order_number>/', views.order_detail, name='order_detail'),
]
