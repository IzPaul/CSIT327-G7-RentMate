from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Sum
from collections import namedtuple
from datetime import datetime
from datetime import date
from decimal import Decimal
from django.db.models import Q
from django.views.decorators.http import require_POST
from .forms import TenantRegisterForm, MaintenanceRequestForm, LandlordMaintenanceUpdateForm, PaymentForm
from .models import Tenant, MaintenanceRequest, Payment, MonthlyBilling
from django.views.decorators.cache import never_cache
from dateutil.relativedelta import relativedelta


# --- LANDLORD SIDE ---

def generate_monthly_billing_records(tenant):
    """
    Generate monthly billing records for a tenant from lease_start to lease_end.
    Each record represents one month's rent due on the 1st of that month.
    """
    current_date = tenant.lease_start
    
    while current_date <= tenant.lease_end:
        # billing_month is the 1st of each month
        billing_month_date = date(current_date.year, current_date.month, 1)
        
        # Due date is the 1st of the month
        due_date = date(current_date.year, current_date.month, 1)
        
        # Calculate total: rent + utilities + other charges
        total = tenant.rent
        balance = total
        
        # Create billing record if it doesn't exist
        MonthlyBilling.objects.get_or_create(
            tenant=tenant,
            billing_month=billing_month_date,
            defaults={
                'rent_amount': tenant.rent,
                'water_bill': Decimal('0.00'),
                'electricity_bill': Decimal('0.00'),
                'other_charges': Decimal('0.00'),
                'total_amount': total,
                'amount_paid': Decimal('0.00'),
                'balance': balance,
                'due_date': due_date,
                'status': 'Unpaid',
                'notes': ''
            }
        )
        
        # Move to next month
        current_date = current_date + relativedelta(months=1)


@login_required(login_url='landlord_login')
def tenant_list_view(request):
    tenants = Tenant.objects.filter(assigned_landlord=request.user)
    query = request.GET.get('q', '').strip()

    if query:
        tenants = tenants.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    status_filter = request.GET.get('status', 'all')
    payment_filter = request.GET.get('payment', 'all')

    if status_filter != 'all':
        tenants = tenants.filter(status__iexact=status_filter)

    if payment_filter != 'all':
        tenants = tenants.filter(payment_status__iexact=payment_filter)

    sort_by = request.GET.get('sort', 'name')
    sort_map = {
        'name': 'first_name',
        'unit': 'unit',
        'start_date': 'lease_start',
        'end_date': 'lease_end',
        'rent': 'rent',
        'payment_status': 'payment_status',
        'rental_status': 'status',
    }
    if sort_by in sort_map:
        tenants = tenants.order_by(sort_map[sort_by])

    return render(request, "home_app/tenant-list.html", {
        'tenants': tenants,
        'search_query': query,
        'current_status': status_filter or 'all',
        'current_payment': payment_filter or 'all',
        'current_sort': sort_by,
    })


import threading

class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            # Create SendGrid email
            mail = Mail(
                from_email=self.from_email,
                to_emails=self.recipient_list,
                subject=self.subject,
                plain_text_content=self.message
            )
            
            # Send via SendGrid API
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(mail)
            print(f"Email sent successfully. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending email in background: {e}")

def tenant_register(request):
    if not request.user.is_authenticated:
        return redirect('landlord_login')

    if request.method == 'POST':
        form = TenantRegisterForm(request.POST)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.assigned_landlord = request.user
            tenant.is_active = False
            tenant.first_login = True
            tenant.status = 'Inactive'
            tenant.save()

            # Generate monthly billing records
            generate_monthly_billing_records(tenant)

            temp_password = form.cleaned_data['password']
            
            # Send email in background to avoid timeout
            email_subject = 'Your Tenant Account - RentMate'
            email_message = f"""
Hi {tenant.first_name},

Your account has been created.

Email: {tenant.email}
Temporary Password: {temp_password}

Please log in at: [https://rentmate-h3m7.onrender.com/home/tenant/login/]

Thank you,
RentMate Team
"""
            EmailThread(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [tenant.email]
            ).start()

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


# --- TENANT LOGIN, LOGOUT & PASSWORD CHANGE ---

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


def tenant_logout(request):
    # Remove tenant id from session
    request.session.pop("tenant_id", None)
    messages.success(request, "You have been logged out successfully")
    return redirect("tenant_login")


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

@never_cache
def tenant_home(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect("tenant_login")

    tenant = Tenant.objects.get(id=tenant_id)
    requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('-date_requested')

    pending_count = requests.filter(request_status='Pending').count()
    approved_count = requests.filter(request_status='Approved').count()
    completed_count = requests.filter(request_status='Completed').count()

    today = datetime.now().date()
    days_remaining = (tenant.lease_end - today).days
    lease_remaining = f"{days_remaining} day{'s' if days_remaining > 1 else ''}"

    total_charges = tenant.monthly_bills.filter(billing_month__lte=date.today().replace(day=1)).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_payments = tenant.payments.filter(status="Approved").aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    outstanding_balance = total_charges - total_payments

    payment_status = ("Paid" if outstanding_balance <= 0 else "Unpaid")

    return render(request, "home_app_tenant/tenant-home.html", {
        "tenant": tenant,
        "requests": requests,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "completed_count": completed_count,
        "payment_status": payment_status,
        "lease_remaining": lease_remaining,
        "outstanding_balance": outstanding_balance,
    })


# --- TENANT MAINTENANCE REQUESTS ---

@never_cache
def tenant_maintenance_list_view(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect('tenant_login')

    tenant = Tenant.objects.get(id=tenant_id)
    requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('-date_requested')

    return render(request, 'home_app_tenant/tenant-maintenance-list.html', {
        "tenant": tenant,
        "requests": requests
    })


@never_cache
def tenant_maintenance_add_view(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect('tenant_login')

    tenant = Tenant.objects.get(id=tenant_id)
    maintenance_requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('-date_requested')[:5]

    if request.method == 'POST':
        problems = request.POST.getlist('problem[]')
        other_description = request.POST.get('other_description', '')
        description = request.POST.get('description', '')

        if problems:
            maintenance_type = ', '.join(problems)
        else:
            messages.error(request, 'Please select at least one problem.')
            return render(request, 'home_app_tenant/tenant-maintenance.html', {
                'tenant': tenant,
                'maintenance_requests': maintenance_requests
            })

        if 'Others' in problems and other_description:
            maintenance_type = maintenance_type.replace('Others', f'Others: {other_description}')

        if not description:
            messages.error(request, 'Please provide a description.')
            return render(request, 'home_app_tenant/tenant-maintenance.html', {
                'tenant': tenant,
                'maintenance_requests': maintenance_requests
            })

        MaintenanceRequest.objects.create(
            requester=tenant,
            date_requested=timezone.localtime().date(),
            maintenance_type=maintenance_type,
            other_description=other_description if 'Others' in problems else '',
            description=description
        )
        messages.success(request, 'Maintenance request submitted successfully!')
        return redirect('tenant_maintenance')

    return render(request, 'home_app_tenant/tenant-maintenance.html', {
        'tenant': tenant,
        'maintenance_requests': maintenance_requests
    })


# --- TENANT PAYMENTS ---

@never_cache
def tenant_payment(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect('tenant_login')

    tenant = Tenant.objects.get(id=tenant_id)
    payments = Payment.objects.filter(tenant=tenant).order_by('-created_at')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            Payment.objects.create(
                tenant=tenant,
                title=form.cleaned_data['title'],
                method=form.cleaned_data['method'],
                amount=form.cleaned_data['amount'],
                reference_number=form.cleaned_data['reference_number'],
            )
            messages.success(request, 'Payment submitted successfully!')
            return redirect('tenant_home')
    else:
        form = PaymentForm()

    return render(request, 'home_app_tenant/tenant-payment.html', {
        'form': form,
        'tenant': tenant,
        'payments': payments,
    })


@never_cache
def tenant_maintenance_edit_view(request, request_id):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
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


@never_cache
def tenant_maintenance_delete_view(request, request_id):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect('tenant_login')

    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, requester_id=tenant_id)

    if maintenance_request.request_status in ["Approved", "Completed"]:
        messages.error(request, "You cannot delete an approved or completed request.")
    else:
        maintenance_request.delete()
        messages.success(request, "Maintenance request deleted successfully!")

    return redirect('tenant_home')

@never_cache
def tenant_lease_view(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        messages.info(request, "Please log in to continue")
        return redirect('tenant_login')
    tenant = get_object_or_404(Tenant, id=tenant_id)

    today = datetime.now().date()
    days_remaining = (tenant.lease_end - today).days
    lease_remaining = f"{days_remaining} day{'s' if days_remaining > 1 else ''}"

    total_charges = tenant.monthly_bills.filter(billing_month__lte=date.today().replace(day=1)).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_payments = tenant.payments.filter(status="Approved").aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    outstanding_balance = total_charges - total_payments

    return render(request, 'home_app_tenant/tenant-lease.html',{
        "tenant": tenant,
        "lease_remaining": lease_remaining,
        "outstanding_balance": outstanding_balance,
    })


# --- LANDLORD MAINTENANCE MANAGEMENT ---

@never_cache
@login_required(login_url='landlord_login')
def home_view(request):
    try:
        # Count active tenants
        active_tenant_count = Tenant.objects.filter(status="Active").count()

        # Calculate monthly revenue
        current_month = date.today().month
        current_year = date.today().year
        monthly_revenue = Payment.objects.filter(
            status="Approved",
            date_verified__month=current_month,
            date_verified__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Count leases ending this month
        lease_renewal_count = Tenant.objects.filter(
            lease_end__month=current_month,
            lease_end__year=current_year
        ).count()

        # Count payments needing verification
        payment_count = Payment.objects.filter(status="Pending").count()

        # Maintenance requests
        requests = MaintenanceRequest.objects.all()
        pending_count = requests.filter(request_status='Pending').count()

        context = {
            'payment_count': Payment.objects.filter(status="Pending").count(),
            'active_tenant_count': active_tenant_count,
            'monthly_revenue': monthly_revenue,
            'lease_renewal_count': lease_renewal_count,
            'payment_count': payment_count,
            'requests': requests,
            'pending_count': pending_count,
        }

        return render(request, "home_app/home.html", context)
    except Exception as e:
        print(f"Error in home_view: {e}")
        raise


@login_required(login_url='landlord_login')
def landlord_maintenance_list_view(request):
    requests = MaintenanceRequest.objects.filter(requester__assigned_landlord=request.user).order_by('-date_requested')
    return render(request, 'home_app/landlord-maintenance-list.html', {'requests': requests})


@login_required(login_url='landlord_login')
def landlord_maintenance_update_view(request, request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)

    if request.method == "POST":
        remarks = request.POST.get("remarks")
        completion_date = request.POST.get("completion_date")

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


# ----- LANDLORD PROOF OF PAYMENTS LIST --------

@login_required(login_url='landlord_login')
def landlord_payments_list_view(request):

    payments = Payment.objects.filter(tenant__assigned_landlord=request.user).order_by('-created_at')

    return render(request, 'home_app/landlord-payments-list.html', {
        "payments": payments
    })


@login_required(login_url='landlord_login')
def landlord_payments_update_view(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    if request.method == "POST":
        status = request.POST.get("status")
        date_verified = request.POST.get("date_verified")

        if date_verified == "":
            date_verified = None

        if status != payment.status or payment.date_verified != date_verified:
            payment.status = status
            payment.date_verified = date_verified
            payment.save()
            return redirect("landlord_payments_list")

    return render(request, 'home_app/landlord-payments-list-update.html',{
        "payment": payment,
    })

@require_POST
def approve_payment(request,payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = "Approved"
    payment.date_verified = datetime.now().date()
    payment.save()
    
    # Update the corresponding monthly bill to "Paid"
    # Use the payment's date_verified to determine which month to mark as paid
    if payment.date_verified:
        try:
            # billing_month is stored as the 1st of each month
            billing_month_date = date(payment.date_verified.year, payment.date_verified.month, 1)
            monthly_bill = MonthlyBilling.objects.get(
                tenant=payment.tenant,
                billing_month=billing_month_date
            )
            monthly_bill.status = "Paid"
            monthly_bill.amount_paid = monthly_bill.total_amount
            monthly_bill.balance = Decimal('0.00')
            monthly_bill.save()
        except MonthlyBilling.DoesNotExist:
            # If no matching monthly bill exists, we can just skip this step
            pass
    
    return redirect('landlord_payments_list')

#Landlord - List of Leases View
@login_required(login_url='landlord_login')
def landlord_leases_view(request):
    tenants = Tenant.objects.filter(assigned_landlord=request.user).order_by('unit').prefetch_related('payments').all()

    LeaseRow = namedtuple('LeaseRow', ['tenant', 'outstanding_balance'])

    lease_data = []
    today = datetime.now().date()

    for tenant in tenants:
        if not tenant.lease_start or not tenant.lease_end:
            outstanding_balance = Decimal('0.00')
        else:
            total_charges = tenant.monthly_bills.filter(billing_month__lte=date.today().replace(day=1)).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            total_payments = tenant.payments.filter(status="Approved").aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            outstanding_balance = total_charges - total_payments

        lease_data.append(LeaseRow(tenant=tenant, outstanding_balance=outstanding_balance))

    return render(request, 'home_app/landlord-leases.html', {
        'lease_data': lease_data,
    })

@login_required(login_url='landlord_login')
def landlord_lease_details_view(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    today = datetime.now().date()
    days_remaining = (tenant.lease_end - today).days
    lease_remaining = f"{days_remaining} day{'s' if days_remaining > 1 else ''}"

    total_charges = tenant.monthly_bills.filter(billing_month__lte=date.today().replace(day=1)).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_payments = tenant.payments.filter(status="Approved").aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    outstanding_balance = total_charges - total_payments

    return render(request, 'home_app/landlord-lease-full-details.html',{
        "tenant": tenant,
        "lease_remaining": lease_remaining,
        "outstanding_balance": outstanding_balance,
    })

# Landlord - Tenant Profile View

@login_required(login_url='landlord_login')
def landlord_tenant_profile_view(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    approved_payments = Payment.objects.filter(tenant=tenant, status="Approved").order_by('date_verified')
    activities = Payment.objects.filter(tenant=tenant).exclude(status="Approved").order_by('created_at')
    requests = MaintenanceRequest.objects.filter(requester=tenant).order_by('date_requested')
    monthly_bills = MonthlyBilling.objects.filter(tenant=tenant).order_by('billing_month')

    return render(request, 'home_app/landlord-tenant-profile.html', {
        "tenant": tenant,
        "approved_payments": approved_payments,
        "activities": activities,
        "requests": requests,
        "monthly_bills": monthly_bills,
    })
