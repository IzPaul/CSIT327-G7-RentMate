"""
WSGI config for RentMateProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from pathlib import Path

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentMateProject.settings')

# Get the WSGI application
application = get_wsgi_application()

# Add WhiteNoise for serving static files in production
application = WhiteNoise(application, root=Path(__file__).resolve().parent.parent / "staticfiles")
application.add_files(Path(__file__).resolve().parent.parent / "static", prefix="static/")