from django.shortcuts import render,redirect
from .models import Product,Category,Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from .models import Contact

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the message to the database
        Contact.objects.create(name=name, email=email, message=message)

        # Show a success message and redirect
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

    return render(request, 'contact.html')



def search(request):
    #check if user filled the form
    if request.method =="POST":
        searched = request.POST.get('searched')
        #query the product db model, icontains is yoused for serach and isnt case sensitive
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched ) | Q(name__icontains=searched ))
        #test for null
        if not searched:
            # messages.success(request, "Search item not found")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched':searched})

    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user_profile = Profile.objects.get(user__id=request.user.id)
        #get current user's shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        #get original userform
        form = UserInfoForm(request.POST or None, instance=current_user_profile)
        #get users shipping form
        shipping_form = ShippingForm(request.POST or None,instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()

            messages.success(request, "User information has been updated")
            return redirect('home')
        return render(request, 'update_info.html', {'form': form,'shipping_form':shipping_form})
    else:  
        messages.success(request,"you must be logged in")
        return redirect('home')
        


def update_password(request):
    if request.user.is_authenticated:                    #check if user is logged in
        current_user = request.user
        if request.method =='POST':                      # if the user filled the fform
            #do stuff
            form = ChangePasswordForm(current_user,request.POST)
            #is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "you password has been updated")
                login(request,current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error)
                return render(request, 'update_password.html', {'form':form})
        else:                                             #if the user is visiting the page
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request, "You must be logged in")
        return redirect('home')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance = current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "user has been updated")
            return redirect('home')
        
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, "You must be logged in")
        return redirect('home')





def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})


def category(request, foo):
    # Replace hyphens with spaces to match category names in the database
    foo = foo.replace('-', ' ')
    try:
        # Perform a case-insensitive lookup for the category
        category = Category.objects.get(name__iexact=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.error(request, "Category doesn't exist.")
        return redirect('home')


def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request,'product.html',{'product':product})

def home(request):
    products = Product.objects.all()
    return render(request,'home.html',{'products':products})

def about(request):
    return render(request,'about.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)

            #do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            #get their saved cart from db
            saved_cart = current_user.old_cart
            #reconvert db string(json) into python dict
            #check if the cart contains item
            if saved_cart:
                #conert to dictionary using json using load keyword
                converted_cart =json.loads(saved_cart)
                #add the loaded cart dictionary to uour section 
                #get the cart
                cart = Cart(request)
                #loop through the cart and add item from db
                for key,value in converted_cart.items():
                    cart.db_add(product=key,quantity=value)




            messages.success(request, ("logged in"))
            return redirect('home')
        else:
            messages.success(request, ("Login failed"))
            return redirect('login')

    else:    
        return render(request,'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, ("you have logged out.."))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #uncomment below codes if i want to login automatically after registering
            #username = form.cleaned_data['username']
            #password = form.cleaned_data['password1']
            #log in user
            #user = authenticate(username=username,password=password)
            #login(request,user)
            messages.success(request, ("you have Registered succesfully"))
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
            return render(request, 'register.html', {'form':form})
           # return redirect('register')
    else:
        return render(request,'register.html',{'form':form})