from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime

from .forms import TenantRegisterForm, MaintenanceRequestForm, LandlordMaintenanceUpdateForm
from .models import Tenant, MaintenanceRequest

# --- LANDLORD SIDE ---

@login_required(login_url='landlord_login')
def tenant_list_view(request):
    tenants = Tenant.objects.all()
    return render(request, "home_app/tenant-list.html", {'tenants': tenants})

def tenant_register(request):
    if not request.user.is_authenticated:
        return redirect('landlord_login')

    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.is_active = False
            tenant.first_login = True
            tenant.status = 'Inactive'
            tenant.save()

            temp_password = form.cleaned_data['password']
            send_mail(
                'Your Tenant Account - RentMate',
                f"""
Hi {tenant.first_name},

Your account has been created.

Email: {tenant.email}
Temporary Password: {temp_password}

Please log in at: http://127.0.0.1:8000/home/tenant/login/

Thank you,
RentMate Team
""",
                settings.EMAIL_HOST_USER,
                [tenant.email],
                fail_silently=False
            )

            messages.success(request, 'Tenant created successfully! Credentials sent via email.')
            return redirect('tenant_list')
    else:
        form = TenantRegisterForm()

    return render(request, 'home_app/tenant-account-register.html', {'form': form})

def edit_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = TenantRegisterForm(request.POST, instance=tenant)
        if form.is_valid():
            if 'password' in form.cleaned_data and form.cleaned_data['password']:
                tenant.password = make_password(form.cleaned_data['password'])
            form.save()
            tenant.save()
            messages.success(request, 'Tenant updated successfully!')
            return redirect('tenant_list')
    else:
        form = TenantRegisterForm(instance=tenant)
    return render(request, 'home_app/tenant-account-register.html', {'form': form, 'edit_mode': True})

def delete_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tenant.delete()
    messages.success(request, 'Tenant deleted successfully.')
    return redirect('tenant_list')

# --- TENANT LOGIN & PASSWORD CHANGE ---

def tenant_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            tenant = Tenant.objects.get(email=email)
        except Tenant.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect("tenant_login")

        if check_password(password, tenant.password):
            request.session["tenant_id"] = tenant.id

            if tenant.first_login:
                messages.info(request, "Update password required.")
                return redirect("tenant_change_password")

            tenant.is_active = True
            tenant.save()
            messages.success(request, f"Welcome back, {tenant.first_name}!")
            return redirect("tenant_home")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("tenant_login")

    return render(request, "logins/tenant-login.html")

def tenant_change_password(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("tenant_login")

    tenant = Tenant.objects.get(id=tenant_id)

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password == confirm_password:
            tenant.password = make_password(password)
            tenant.first_login = False
            tenant.is_active = True
            tenant.save()
            messages.success(request, "Password updated successfully! You can now login.")
            return redirect("tenant_login")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "home_app/tenant-change-password.html")

# --- TENANT DASHBOARD ---

def tenant_home(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("tenant_login")

    tenant = Tenant.objects.get(id=tenant_id)
    requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('-date_requested')

    pending_count = requests.filter(request_status='Pending').count()
    approved_count = requests.filter(request_status='Approved').count()
    completed_count = requests.filter(request_status='Completed').count()

    return render(request, "home_app_tenant/tenant-home.html", {
        "tenant": tenant,
        "requests": requests,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "completed_count": completed_count,
    })

# --- TENANT MAINTENANCE REQUESTS ---

def tenant_maintenance_list_view(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect('tenant_login')

    tenant = Tenant.objects.get(id=tenant_id)
    requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('-date_requested')

    return render(request, 'home_app_tenant/tenant-maintenance-list.html', {
        "tenant": tenant,
        "requests": requests
    })

def tenant_maintenance_add_view(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect('tenant_login')

    tenant = Tenant.objects.get(id=tenant_id)

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            MaintenanceRequest.objects.create(
                requester=tenant,
                date_requested=timezone.localtime().date(),
                maintenance_type=form.cleaned_data['maintenance_type'],
                other_description=form.cleaned_data['other_description'],
                description=form.cleaned_data['description']
            )
            messages.success(request, 'Maintenance request created successfully!')
            return redirect('tenant_home')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'home_app_tenant/tenant-maintenance.html', {'form': form})

def tenant_maintenance_edit_view(request, request_id):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect('tenant_login')

    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, requester_id=tenant_id)

    if maintenance_request.request_status in ["Approved", "Completed"]:
        messages.error(request, "You cannot edit an approved or completed request.")
        return redirect('tenant_home')

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=maintenance_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Maintenance request updated successfully!")
            return redirect('tenant_home')
    else:
        form = MaintenanceRequestForm(instance=maintenance_request)

    return render(request, 'home_app_tenant/tenant-maintenance-edit.html', {'form': form})

def tenant_maintenance_delete_view(request, request_id):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect('tenant_login')

    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, requester_id=tenant_id)

    if maintenance_request.request_status in ["Approved", "Completed"]:
        messages.error(request, "You cannot delete an approved or completed request.")
    else:
        maintenance_request.delete()
        messages.success(request, "Maintenance request deleted successfully!")

    return redirect('tenant_home')

# --- LANDLORD MAINTENANCE MANAGEMENT ---

@login_required(login_url='landlord_login')
def home_view(request):
    requests = MaintenanceRequest.objects.all()
    pending_count = requests.filter(request_status='Pending').count()

    context = {
        'requests': requests,
        'pending_count': pending_count,
    }
    return render(request, "home_app/home.html", context)

@login_required(login_url='landlord_login')
def landlord_maintenance_list_view(request):
    requests = MaintenanceRequest.objects.all().order_by('-date_requested')
    return render(request, 'home_app/landlord-maintenance-list.html', {'requests': requests})

@login_required(login_url='landlord_login')
def landlord_maintenance_update_view(request, request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)

    if request.method == "POST":
        remarks = request.POST.get("remarks")
        completion_date = request.POST.get("completion_date")  # string YYYY-MM-DD

        maintenance_request.remarks = remarks

        if remarks == "Done":
            maintenance_request.request_status = "Completed"
            if completion_date:
                maintenance_request.completion_date = datetime.strptime(completion_date, "%Y-%m-%d").date()
            else:
                maintenance_request.completion_date = timezone.localtime().date()
        elif remarks == "Canceled":
            maintenance_request.request_status = "Canceled"
            maintenance_request.completion_date = None
        else:
            maintenance_request.request_status = "Pending"
            if completion_date:
                maintenance_request.completion_date = datetime.strptime(completion_date, "%Y-%m-%d").date()
            else:
                maintenance_request.completion_date = None

        maintenance_request.save()
        messages.success(request, "Maintenance request updated successfully.")
        return redirect("landlord_maintenance_list")

    return render(request, "home_app/landlord-maintenance-update.html", {
        "request_item": maintenance_request
    })
