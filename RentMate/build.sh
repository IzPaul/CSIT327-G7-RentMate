#!/usr/bin/env bash
# Exit on error
set -o errexit
set -o pipefail

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create necessary directories
mkdir -p staticfiles

# Set the DJANGO_SETTINGS_MODULE environment variable
export DJANGO_SETTINGS_MODULE=RentMateProject.settings

# Collect static files with debugging
python manage.py collectstatic --no-input --clear

# Set proper permissions for static files
chmod -R 755 staticfiles/
