#!/usr/bin/env bash
# Exit on error
set -o errexit
set -o pipefail

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Set the DJANGO_SETTINGS_MODULE environment variable
export DJANGO_SETTINGS_MODULE=RentMateProject.settings

# Create necessary directories
mkdir -p staticfiles

# Collect static files with debugging
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "Static files collected."

# Set proper permissions for static files
chmod -R 755 staticfiles/

# Create a test file to verify static files
echo "Static files collected at: $(date)" > staticfiles/static_test.txt