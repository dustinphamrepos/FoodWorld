from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('<slug:vendor_slug>/<int:pk>/', views.vendor_detail_by_category, name='vendor_detail_by_category'),
]
