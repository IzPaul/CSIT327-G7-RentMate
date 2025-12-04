"""
Test script to verify SendGrid email functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentMateProject.settings')
django.setup()

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def test_sendgrid_email():
    """Send a test email using SendGrid"""
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails='test@example.com',  # Replace with your test email
            subject='RentMate - SendGrid Test Email',
            plain_text_content='This is a test email sent via SendGrid API from RentMate!'
        )
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    print("Testing SendGrid email configuration...")
    print(f"Using API Key: {settings.SENDGRID_API_KEY[:10]}...")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    print("-" * 50)
    test_sendgrid_email()
