# Generated manually for fixing maintenance_type max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenancerequest',
            name='maintenance_type',
            field=models.CharField(max_length=200),
        ),
    ]
