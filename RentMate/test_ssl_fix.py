"""
SendGrid Test with SSL fix for Windows
"""
import os
import ssl
import certifi

# Fix SSL certificate verification
os.environ['SSL_CERT_FILE'] = certifi.where()

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

print("=" * 70)
print("SendGrid Email Test - RentMate (SSL Fixed)")
print("=" * 70)

FROM_EMAIL = 'rrentmate@gmail.com'
TO_EMAIL = 'rrentmate@gmail.com'

message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject='✅ RentMate - SendGrid Working!',
    html_content='''
    <html>
        <body style="font-family: Arial; padding: 30px; background: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; 
                        padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #27ae60; text-align: center;">🎉 Success!</h1>
                <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #2c3e50;">SendGrid is Working!</h2>
                    <p><strong>Your email system is ready!</strong></p>
                </div>
                <ul style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <li>✅ API Key: Valid</li>
                    <li>✅ Sender: Verified</li>
                    <li>✅ Email Delivery: Working</li>
                </ul>
                <p style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
                    RentMate • SendGrid API
                </p>
            </div>
        </body>
    </html>
    '''
)

try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    
    print("\n✅✅✅ EMAIL SENT SUCCESSFULLY! ✅✅✅\n")
    print(f"Status: {response.status_code}")
    print(f"\n📧 Check your Gmail: {TO_EMAIL}")
    print("⚠️  Look in SPAM folder if not in inbox\n")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    print("=" * 70)
