"""
Automated SendGrid Email Test - No input required
Tests email sending with your new API key
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Email configuration
FROM_EMAIL = 'rrentmate@gmail.com'  # Your verified sender
TO_EMAIL = 'rrentmate@gmail.com'  # Send to yourself for testing

print("=" * 70)
print("SendGrid Email Test - RentMate")
print("=" * 70)
print(f"From: {FROM_EMAIL}")
print(f"To: {TO_EMAIL}")
print(f"API Key: {os.environ.get('SENDGRID_API_KEY')[:20]}...")
print("-" * 70)

# Create test email
message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject='🎉 RentMate - SendGrid Test Email',
    html_content='''
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; 
                        padding: 20px; border: 2px solid #3498db; border-radius: 10px;">
                <h1 style="color: #27ae60; text-align: center;">✅ SendGrid Works!</h1>
                
                <div style="background-color: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #2c3e50; margin-top: 0;">Success!</h2>
                    <p><strong>Your SendGrid API is configured correctly!</strong></p>
                    <p>This email was sent using SendGrid's API with your new API key.</p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>✨ What this means:</strong></p>
                    <ul>
                        <li>✅ API Key is valid and working</li>
                        <li>✅ Sender email is verified</li>
                        <li>✅ Emails will be delivered to tenants</li>
                    </ul>
                </div>
                
                <p style="text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                    RentMate • Powered by SendGrid
                </p>
            </div>
        </body>
    </html>
    '''
)

try:
    # Send email
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    
    print("\n" + "=" * 70)
    if response.status_code == 202:
        print("✅✅✅ EMAIL SENT SUCCESSFULLY! ✅✅✅")
        print("=" * 70)
        print(f"\n🎉 SendGrid accepted your email!")
        print(f"📧 Check your inbox: {TO_EMAIL}")
        print(f"⚠️  If not in inbox, check your SPAM/JUNK folder")
        print(f"\n📊 Status Code: {response.status_code} (Accepted)")
        print(f"📨 Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
        print("\n✅ Your RentMate email system is READY!")
        print("   Tenants will receive their credentials via email!")
    else:
        print(f"⚠️  Status Code: {response.status_code}")
        print(f"Response: {response.body}")
    print("=" * 70)

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR")
    print("=" * 70)
    print(f"Error: {str(e)}")
    
    if "Unauthorized" in str(e):
        print("\n💡 FIX: API key is invalid")
        print("   Create a new one at: https://app.sendgrid.com/settings/api_keys")
    elif "does not contain a valid address" in str(e) or "Forbidden" in str(e):
        print("\n💡 FIX: Sender email not verified")
        print("   Verify at: https://app.sendgrid.com/settings/sender_auth")
        print(f"   Email: {FROM_EMAIL}")
    else:
        print("\n💡 Check SendGrid dashboard for details:")
        print("   https://app.sendgrid.com/email_activity")
    
    print("=" * 70)
