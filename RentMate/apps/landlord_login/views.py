from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from .models import LandlordProfile
from .forms import LandlordRegistrationForm
from ..dashboard.models import Tenant
import logging

# Initialize logger
logger = logging.getLogger(__name__)


def landlord_login(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            # Try to authenticate using Django's built-in authentication
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if user is a landlord
                try:
                    landlord_profile = LandlordProfile.objects.get(user=user)
                    login(request, user)
                    logger.info(f"Landlord {user.email} logged in successfully")
                    return redirect('home')  # Redirect to dashboard
                except LandlordProfile.DoesNotExist:
                    messages.error(request, 'Account not found or not a landlord account')
                    logger.warning(f"Login attempt with landlord account but no profile: {email}")
            else:
                messages.error(request, 'Invalid Credentials')
                logger.warning(f"Failed login attempt for email: {email}")
        except Exception as e:
            logger.exception(f"Unexpected error during landlord login for {request.POST.get('email')}")
            messages.error(request, 'An unexpected error occurred. Please try again later.')

    return render(request, 'logins/landlord-login.html')

def tenant_login(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            #User authentication
            user = authenticate(request, username=email, password=password)

            if user is not None:
                try:
                    tenant = Tenant.objects.get(user=user)
                    login(request, user)
                    logger.info(f"Tenant {user.email} logged in successfully")
                    return redirect('tenant_home')  # Redirect to dashboard
                except Tenant.DoesNotExist:
                    messages.error(request, 'Account not found or not a tenant account')
                    logger.warning(f"Login attempt with tenant account but no profile: {email}")
            else:
                messages.error(request, 'Invalid Credentials')
                logger.warning(f"Failed login attempt for email: {email}")
        except Exception as e:
            logger.exception(f"Unexpected error during tenant login for {request.POST.get('email')}")
            messages.error(request, 'An unexpected error occurred. Please try again later.')

    return render(request, 'logins/tenant-login.html')

def index(request):
    return render(request, 'index.html')  # This will look in the root templates directory first

@transaction.atomic #If an error occurs within the block, no changes is saved to the database
def landlord_register(request):
    if request.method == 'POST':
        form = LandlordRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create User
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )

                # Create Landlord Profile
                LandlordProfile.objects.create(
                    user=user,
                    address=form.cleaned_data['address'],
                    phone_number=form.cleaned_data['phone_number']
                )
                messages.success(request, 'Registration successful! Please login.')
                logger.info(f"New landlord registered: {form.cleaned_data.get('first_name')} {form.cleaned_data.get('last_name')}")
                return redirect('landlord_login')

            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')
                logger.error(f"Registration error: {str(e)}")

        else:
            # Convert form errors to messages
            for field_name, field_errors in form.errors.items():
                for error in field_errors:
                    clean_error = error.strip()
                    print(f"Error in {field_name}: {clean_error}")
                    if field_name == '__all__':
                        messages.error(request, clean_error)
                    else:
                        messages.error(request, f"{clean_error}")
    else:
        form = LandlordRegistrationForm()

    return render(request, 'logins/landlord-register.html', {'form': form})



