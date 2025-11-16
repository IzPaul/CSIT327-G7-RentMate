from django.contrib import admin
from .models import Tenant, MaintenanceRequest, Payment

# Register your models here.
admin.site.register(Tenant)
admin.site.register(MaintenanceRequest)
admin.site.register(Payment)