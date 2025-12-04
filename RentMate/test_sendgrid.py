"""
Test script to verify SendGrid email functionality
Following SendGrid's official Python documentation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentMateProject.settings')
django.setup()

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def test_sendgrid_email():
    """Send a test email using SendGrid following official documentation"""
    
    # Create HTML email message
    message = Mail(
        from_email='rrentmate@gmail.com',  # Your verified sender
        to_emails='test@example.com',  # Replace with your test email
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>'
    )
    
    try:
        # Initialize SendGrid client with API key from environment
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Send the email
        response = sg.send(message)
        
        # Print success information
        print("✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing SendGrid Email Configuration")
    print("=" * 60)
    print(f"Using API Key: {os.environ.get('SENDGRID_API_KEY', 'NOT SET')[:15]}...")
    print(f"From Email: rrentmate@gmail.com")
    print("-" * 60)
    test_sendgrid_email()
    print("=" * 60)
