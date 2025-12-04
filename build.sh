#!/bin/bash

# RentMate Render Deploy Script
# This script handles the migration issue where dashboard_monthlybilling already exists

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Faking 0002_monthlybilling migration (table already exists)..."
python manage.py migrate dashboard 0002_monthlybilling --fake

echo "==> Running remaining migrations..."
python manage.py migrate

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
gunicorn RentMateProject.wsgi:application --log-file -
