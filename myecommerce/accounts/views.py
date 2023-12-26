
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse

from products.models import Product, SizeVariant
# Create your views here.
from .models import CartItems, Profile,Cart
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# from .models import CartItems
import razorpay

def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')
    

def add_to_cart(request,uid):
    
    variant=request.GET.get('variant')
    product=Product.objects.get(uid=uid)
    user=request.user
    cart , _=Cart.objects.get_or_create(user=user,is_paid=False) 
    cart_item=CartItems.objects.create(cart=cart,product=product) 
    if variant:
        variant=request.GET.get('variant')
        size_variant=SizeVariant.objects.get(size_name=variant) 
        cart_item.size_variant=size_variant
        cart_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  


def remove_cart(request,cart_item_uid):
    try:
        cart_item=CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()

    except Exception as e:
        print(e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))    



from django.conf import settings

def cart(request):
    try:   
         user_cart = Cart.objects.get(user=request.user,is_paid=False)
    except Exception as e:
        print(e)     
    cart_total = user_cart.get_cart_total()
    cart_items = CartItems.objects.filter(cart=user_cart)
    context={'cart_items' :cart_items,'cart_total':cart_total,
             }
    payment=None
    if(user_cart):
        client =razorpay.Client(auth=(settings.KEY,settings.SECRET))
        payment=client.order.create({'amount':cart_total*100,'currency':'INR','payment_capture':1})
        user_cart.razor_pay_order_id=payment['id']
        user_cart.save()

    context={'cart_items' :cart_items,
            'cart_total':cart_total,
            'payment':payment
            }
    print('########',payment,'###########')
    return render(request,'accounts/cart.html',context)

def order(request):
      
    user_cart = Cart.objects.get(user=request.user,is_paid=True)
    
    
    cart_items = CartItems.objects.filter(cart=user_cart)
    
    context={
        'cart_items' :cart_items
            
        }
    
    return render(request,'accounts/order.html',context)

def success(request):
    try:
        order_id = request.GET.get('razorpay_order_id')
        cart = get_object_or_404(Cart, razor_pay_order_id=order_id)
        cart.is_paid = True
        cart.save()
        return redirect('order')  # Replace 'success_page' with the actual URL or view name
    except Cart.DoesNotExist:
        return HttpResponse('Invalid Order ID', status=400)

    