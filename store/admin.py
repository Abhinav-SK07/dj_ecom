from django.contrib import admin
from . models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)

# combine profile info and user info

class ProfileInline(admin.StackedInline):
    model = Profile

# extend user model

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username','first_name','last_name','email']
    inlines = [ProfileInline]

# unregister old-way

admin.site.unregister(User)

# register new-way

admin.site.register(User, UserAdmin)