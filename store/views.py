from django.shortcuts import render,redirect
from .models import Product, Category, Profile
from cart.cart import Cart
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django import forms
from django.db.models import Q
import json

# Create your views here.

def search(request):
    # determine whether they filled the form
    if request.method == 'POST':
        searched = request.POST['searched']
        # query the product / model
        searched = Product.objects.filter(Q(name__icontains=searched)|Q(description__icontains=searched))
        # test for null
        if not searched:
            messages.success(request, "Sorry, The Searched Product Is Not Found... Please Try Again.")
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})

def update_userinfo(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your Info Has Been Updated!")
            return redirect('home')
        return render(request, 'update_userinfo.html', {'form': form})
    else:
        messages.success(request, "You must be logged in first!")
        return redirect('home')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # check if the form is valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user) 
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, "You must be logged in first!")
        return redirect('home')
    
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User has been updated!")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.success(request, "You must be logged in first!")
        return redirect('home')

def category(request, cat):
    #replace hyphons with space
    cat = cat.replace("-", " ")
    #grab the category from the url
    try:
        #lookup the category
        category = Category.objects.get(name=cat)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("category doesn't exist!"))
        return redirect('home')
        
def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html',{'categories': categories})    

def product(request, pk):
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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # get their saved cart from db
            saved_cart = current_user.old_cart
            # convert db string to py dict
            if saved_cart:
                # convert to dict using JSON
                converted_cart = json.loads(saved_cart)
                # add the loaded cart dict to session
                cart = Cart(request)
                # loop thru cart and add the items from db
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ("You have been logged in!"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, try again..."))
            return redirect('login')
    else:
        return render(request, 'login.html')
    
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out!"))
    return redirect('home')

def register(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("User Name Created, Please Fillout Your User Info Below..."))
            return redirect('update_userinfo')
        else:
            messages.success(request, ("Oops... There Was A Problem! Please Try Again..."))
            return redirect('register')
    else:    
        return render(request, 'register.html', {'form':form})