from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('update-cart/<int:pk>/', views.update_cart, name='update_cart'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]
