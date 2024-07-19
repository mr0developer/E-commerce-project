from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import Product, Cart, CartItem, Order, OrderItem, CartItem, Category, Review
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})
@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    return render(request, 'shop/cart.html', {'items': items})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=sum(item.product.price * item.quantity for item in items))
        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            item.delete()
        return redirect('order_history')
    return render(request, 'shop/checkout.html', {'items': items})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_history.html', {'orders': orders})
def product_list(request, category_id=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)
    return render(request, 'shop/product_list.html', {'category': category, 'categories': categories, 'products': products})
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('product_list')
    return render(request, 'shop/add_review.html', {'product': product})