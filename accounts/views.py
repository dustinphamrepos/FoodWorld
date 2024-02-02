from django.contrib import messages
from django.shortcuts import redirect, render

from vendor.forms import VendorForm

from .models import User, UserProfile
from .forms import UserForm

# Create your views here.
def registerUser(request):
  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():
      # Create a new user using the form data
      # password = form.cleaned_data['password']
      # user = form.save(commit=False)
      # user.set_password(password)
      # user.role = User.CUSTOMER
      # user.save()

      # Create a new user using the create_user method of models.py
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      username = form.cleaned_data['username']
      email = form.cleaned_data['email']
      password = form.cleaned_data['first_name']
      user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
      user.role = User.CUSTOMER
      user.save()
      messages.success(request, 'Your account has been registered successfully.')

      return redirect('registerUser')
    else:
      print('Invalid form')
      print(form.errors)
  else:
    form = UserForm()
  context = {
      'form': form,
    }  
  return render(request, 'accounts/registerUser.html', context=context)

def registerVendor(request):
  if request.method == 'POST':
    form = UserForm(request.POST)
    vendor_form = VendorForm(request.POST, request.FILES)
    if form.is_valid() and vendor_form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      username = form.cleaned_data['username']
      email = form.cleaned_data['email']
      password = form.cleaned_data['first_name']
      user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
      user.role = User.VENDOR
      user.save()

      vendor = vendor_form.save(commit=False)
      vendor.user = user
      user_profile = UserProfile.objects.get(user=user)
      vendor.user_profile = user_profile
      vendor.save()
      messages.success(request, 'Your account has been created successfully. Please wait for the approval!')
      return redirect('registerVendor')
    else:
      print("Invalid form")
      print(form.errors)
      return redirect('registerVendor')
  else:
    form = UserForm()
    vendor_form = VendorForm()
    context = {
      'form': form,
      'vendor_form': vendor_form
    }
    
    return render(request, 'accounts/registerVendor.html', context=context)