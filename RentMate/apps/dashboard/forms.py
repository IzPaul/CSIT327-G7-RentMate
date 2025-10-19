from django import forms
from .models import Tenant, MaintenanceRequest
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

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if not self.instance:
            self.fields['password'].initial = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Tenant.objects.filter(email=email, is_active=True)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise forms.ValidationError('Email is already used by an active tenant.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if re.search(r'[^A-Za-z]', first_name):
            raise forms.ValidationError('First name cannot contain numbers or special characters.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if re.search(r'[^A-Za-z]', last_name):
            raise forms.ValidationError('Last name cannot contain numbers or special characters.')
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if re.search(r'[a-zA-Z]', phone_number):
            raise forms.ValidationError('Phone number must not contain letters.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        lease_start = cleaned_data.get('lease_start')
        lease_end = cleaned_data.get('lease_end')
        if lease_start and lease_end and lease_end < lease_start:
            raise forms.ValidationError("Lease end date cannot be before start date.")
        return cleaned_data

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
        required=True,
        choices=MAINTENANCE_CHOICES,
        label="Choose a Maintenance Option",
        widget=forms.Select(attrs={'class': 'form-group'})
    )
    other_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'If others, please provide a description','rows': 2})
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Enter description of the Issue','rows': 4})
    )

    class Meta:
        model = MaintenanceRequest
        fields = ['maintenance_type', 'other_description', 'description']
