from django import forms
from .models import Tenant, MaintenanceRequest, Payment
import re
from django.contrib.auth.hashers import make_password

class TenantRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Tenant
        fields = [
            'email', 'first_name', 'last_name', 'address', 'phone_number',
            'password', 'unit', 'lease_start', 'lease_end', 'rent', 'deposit',
            'payment_status', 'contract_url', 'status'
        ]
        widgets = {
            'lease_start': forms.DateInput(attrs={'type': 'date'}),
            'lease_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Tenant.objects.filter(email=email)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise forms.ValidationError('Email already used by another tenant.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if re.search(r'[^A-Za-z]', first_name):
            raise forms.ValidationError('First name cannot contain numbers or symbols.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if re.search(r'[^A-Za-z]', last_name):
            raise forms.ValidationError('Last name cannot contain numbers or symbols.')
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if re.search(r'[a-zA-Z]', phone_number):
            raise forms.ValidationError('Phone number must not contain letters.')
        return phone_number

    def save(self, commit=True):
        tenant = super().save(commit=False)
        tenant.password = make_password(self.cleaned_data['password'])
        if commit:
            tenant.save()
        return tenant


class MaintenanceRequestForm(forms.ModelForm):
    MAINTENANCE_CHOICES = [
        ('Plumbing', 'Plumbing'),
        ('Electrical', 'Electrical'),
        ('Appliance', 'Appliance'),
        ('Structural', 'Structural'),
        ('Others', 'Others'),
    ]
    maintenance_type = forms.ChoiceField(
        choices=MAINTENANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    other_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'If Others, describe...', 'rows': 2})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe the issue...', 'rows': 4})
    )

    class Meta:
        model = MaintenanceRequest
        fields = ['maintenance_type', 'other_description', 'description']


class LandlordMaintenanceUpdateForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
    ]
    request_status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    completion_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = MaintenanceRequest
        fields = ['request_status', 'completion_date', 'remarks']


class PaymentForm(forms.ModelForm):
    METHOD_CHOICES = [
        ("BPI", "BPI"),
        ("BDO", "BDO"),
        ("GCash", "GCash"),
        ("Other", "Other"),
    ]

    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Payment Title'}))
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.Select())
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    reference_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Reference Number'}))

    class Meta:
        model = Payment
        fields = ['title', 'method', 'amount', 'reference_number']

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Payment Title is required.')
        return title

    def clean_reference_number(self):
        ref = self.cleaned_data.get('reference_number', '').strip()
        if not re.match(r'^[A-Za-z0-9\-]{6,50}$', ref):
            raise forms.ValidationError('Reference Number must be 6-50 chars, letters/numbers/dashes only.')
        return ref
