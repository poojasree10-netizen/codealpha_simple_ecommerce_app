from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product


# -----------------------------
# HOME PAGE – PRODUCT LIST
# -----------------------------
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


# -----------------------------
# PRODUCT DETAIL PAGE
# -----------------------------
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})


# -----------------------------
# ADD TO CART (SESSION BASED)
# -----------------------------
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    product_id = str(product.id)

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    return redirect('cart')


# -----------------------------
# VIEW CART
# -----------------------------
def cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    for product in products:
        cart_items.append({
            'product': product,
            'quantity': cart[str(product.id)]
        })

    return render(request, 'store/cart.html', {'cart_items': cart_items})


# -----------------------------
# USER LOGIN
# -----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid username or password'})

    return render(request, 'store/login.html')


# -----------------------------
# USER REGISTER
# -----------------------------
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'store/register.html')


# -----------------------------
# USER LOGOUT
# -----------------------------
def logout_view(request):
    logout(request)
    return redirect('login')
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    order = Order.objects.create(user=request.user)

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

    request.session['cart'] = {}
    return render(request, 'store/order_success.html', {'order': order})
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total
    })
def checkout(request):
    return render(request, 'store/checkout.html')
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    order = Order.objects.create(user=request.user)

    for product_id, quantity in cart.items():
        OrderItem.objects.create(
            order=order,
            product_id=product_id,
            quantity=quantity
        )

    request.session['cart'] = {}

    return render(request, 'store/order_success.html')

