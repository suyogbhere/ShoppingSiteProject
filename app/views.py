# from django.http import request
from django.db.models import Q
from django.shortcuts import render,redirect
from django. views import View
from .models import Customer,Cart,Product,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django .http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# def home(request):                                # Function Based view
#  return render(request, 'app/home.html')

class ProductView(View):                            # class based view
    def get(self,request):
        totalitem = 0
        topwears=Product.objects.filter(category='TW')
        bottomwears=Product.objects.filter(category='BW')
        mobiles=Product.objects.filter(category='M')
        laptops=Product.objects.filter(category='L')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'laptops':laptops,'totalitem':totalitem})

# def product_detail(request):                          # Function Based view
#  return render(request, 'app/productdetail.html')

class ProductDetail(View):
    def get(self, request, pk):
        totalitem = 0
        product=Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()

        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    # return render(request, 'app/addtocart.html')
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user=user)
        # print(cart)
        totalitem = 0
        amount=0.0
        shipping_amount=70.0
        total_amount=0.0
        cart_product=[p for p in Cart.objects.all() if p.user == user]
        print(cart_product)
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 
        if cart_product:
            for p in cart_product:
                tempamount=(p.quantity * p.product.discounted_price)
                amount+=tempamount
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount,'totalitem':totalitem})
        else:
            return render(request,'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount
            
        data={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount
            
        data={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount=0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount
            
        data={
            'amount': amount,
            'totalamount':amount + shipping_amount
            }
        return JsonResponse(data)



def buy_now(request):
    return render(request, 'app/buynow.html')

# def profile(request):
#  return render(request, 'app/profile.html')

@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'})

@login_required
def orders(request):
    totalitem = 0
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_Placed':op,'totalitem':totalitem})

# def change_password(request):
#  return render(request, 'app/changepassword.html')

def mobile(request,data=None):          
    if data==None:
        mobiles=Product.objects.filter(category='M')               # mobile filter
    elif data =='Redmi' or data == 'Realme':
        mobiles=Product.objects.filter(category='M').filter(brand=data)       # brand filter
    elif data == 'Below':
        mobiles=Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'Above':
        mobiles=Product.objects.filter(category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html',{'mobiles':mobiles})

# def login(request):
#  return render(request, 'app/login.html')


class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',{'form':form})

    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congratulations!! registered successfully')
            form.save()
        return render(request, 'app/customerregistration.html',{'form':form})


# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')
@login_required
def checkout(request):
    totalitem = 0
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 
    amount = 0.0
    shipping_amount = 70
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+=tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_items,'totalitem':totalitem})

@login_required
def payment_done(request):
    user=request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user = user,customer = customer,product = c.product ,quantity = c.quantity).save()
        c.delete()
    return redirect('orders')


def topwear(request,data=None):
    if data == None:
        topwear=Product.objects.filter(category='TW')
    elif data == 'Mens' or data == 'Womens':
        topwear=Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'Below':
        topwear=Product.objects.filter(category='TW').filter(discounted_price__lt=500)
    elif data == 'Above':
        topwear=Product.objects.filter(category='TW').filter(discounted_price__gt=1000)
    return render(request,'app/topwear.html',{'topwear':topwear})


def bottomwear(request,data=None):
    if data == None:
        bottomwear=Product.objects.filter(category='BW')
    elif data == 'Mens' or data == 'Womens':
        bottomwear=Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'Below':
        bottomwear=Product.objects.filter(category='BW').filter(discounted_price__lt=500)
    elif data == 'Above':
        bottomwear=Product.objects.filter(category='BW').filter(discounted_price__gt=1000)
    return render(request,'app/bottomwear.html',{'bottomwear':bottomwear})


def laptop(request,data=None):          
    if data==None:
        laptop=Product.objects.filter(category='L')               # mobile filter
    elif data =='dell' or data == 'HP':
        laptop=Product.objects.filter(category='L').filter(brand=data)       # brand filter
    elif data == 'Below':
        laptop=Product.objects.filter(category='L').filter(discounted_price__lt=30000)
    elif data == 'Above':
        laptop=Product.objects.filter(category='L').filter(discounted_price__gt=30000)
    return render(request, 'app/laptop.html',{'laptops':laptop})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self,request):
        totalitem = 0
        form=CustomerProfileForm()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user)) 
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})

    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulation!! Profile Updated Successfully')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})