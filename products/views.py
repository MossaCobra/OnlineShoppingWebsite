from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        item_total = product.price * int(quantity)
        total_price += item_total
        cart_items.append({'product': product, 'quantity': quantity, 'item_total': item_total})

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    cart[pk] = cart.get(pk, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect(request.META['HTTP_REFERER'])
    pass


def update_cart(request, pk):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity'))

    if quantity > 0:
        cart[pk] = quantity
    else:
        cart.pop(pk, None)

    request.session['cart'] = cart
    return redirect('products:view_cart')


def get_cart_items_and_total(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        item_total = product.price * int(quantity)
        total_price += item_total
        cart_items.append({'product': product, 'quantity': quantity, 'item_total': item_total})

    return cart_items, total_price


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart: 
        cart.pop(str(pk))
        request.session['cart'] = cart

    return redirect('products:view_cart')


def checkout_view(request):
    cart_items, total_price = get_cart_items_and_total(request)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'aud',
                    'product_data': {
                        'name': 'Total Amount',
                    },
                    'unit_amount': int(total_price * 100),
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url='https://e39e-103-138-245-72.ngrok-free.app/checkout/success/',
        cancel_url=request.build_absolute_uri(reverse('products:view_cart')),
    )

    return redirect(session.url)


def checkout_success_view(request):
    return render(request, 'products/checkout_success.html')


@csrf_exempt
def stripe_webhook(request):
    if request.method == 'POST':
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)

            return JsonResponse({'status': 'success'})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
