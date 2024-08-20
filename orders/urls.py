from django.urls import path
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payments-by-momo/', views.payments_by_momo, name='payments_by_momo'),
    path('order-complete/', views.order_complete, name='order_complete'),
]
