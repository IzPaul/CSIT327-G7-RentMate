"""
Quick SendGrid Email Test
Run this to verify your SendGrid setup is working
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Email configuration
FROM_EMAIL = 'rrentmate@gmail.com'  # Your verified sender
TO_EMAIL = input("Enter YOUR email address to receive test: ").strip()

if not TO_EMAIL or '@' not in TO_EMAIL:
    print("❌ Invalid email address!")
    exit(1)

print(f"\n📧 Sending test email to: {TO_EMAIL}")
print("=" * 60)

# Create HTML email
message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject='🎉 RentMate - SendGrid Test Successful!',
    html_content=f'''
    <html>
        <body style="font-family: Arial, sans-serif; padding: 30px; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; 
                        padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #27ae60; text-align: center;">✅ Success!</h1>
                <h2 style="color: #2c3e50;">SendGrid is Working!</h2>
                
                <div style="background-color: #e8f5e9; padding: 20px; border-left: 4px solid #27ae60; margin: 20px 0;">
                    <p style="margin: 0;"><strong>✨ Your SendGrid configuration is correct!</strong></p>
                    <p style="margin: 10px 0 0 0;">Emails from RentMate will now be delivered successfully.</p>
                </div>
                
                <h3 style="color: #2c3e50;">Test Details:</h3>
                <ul style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                    <li><strong>From:</strong> {FROM_EMAIL}</li>
                    <li><strong>To:</strong> {TO_EMAIL}</li>
                    <li><strong>SendGrid API:</strong> Connected ✅</li>
                    <li><strong>Sender Verified:</strong> Yes ✅</li>
                </ul>
                
                <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🎯 What's Next?</strong></p>
                    <p style="margin: 10px 0 0 0;">When landlords create tenant accounts, credentials will be automatically sent via email!</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="text-align: center; color: #7f8c8d; font-size: 12px;">
                    Sent from RentMate using SendGrid API<br>
                    If you received this email, everything is working perfectly! 🚀
                </p>
            </div>
        </body>
    </html>
    '''
)

try:
    # Get API key from environment
    api_key = os.environ.get('SENDGRID_API_KEY')
    
    if not api_key:
        print("❌ ERROR: SENDGRID_API_KEY environment variable not set!")
        print("\nRun this first:")
        print('$env:SENDGRID_API_KEY="your_sendgrid_api_key_here"')
        exit(1)
    
    # Send email
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    
    # Check response
    print("\n" + "=" * 60)
    print("✅ EMAIL SENT SUCCESSFULLY!")
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 202:
        print("\n🎉 SUCCESS! SendGrid accepted your email!")
        print(f"\n📬 Check your inbox: {TO_EMAIL}")
        print("⚠️  If not in inbox, check SPAM folder")
        print("\n✅ Your SendGrid setup is working perfectly!")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")
        print(f"Response: {response.body}")
    
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print("❌ ERROR SENDING EMAIL")
    print("=" * 60)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    
    if "Unauthorized" in str(e) or "401" in str(e):
        print("\n💡 FIX: Your API key may be invalid")
        print("   → Check: https://app.sendgrid.com/settings/api_keys")
    elif "does not contain a valid address" in str(e) or "403" in str(e):
        print("\n💡 FIX: Sender email not verified")
        print("   → Verify: https://app.sendgrid.com/settings/sender_auth")
        print(f"   → Email to verify: {FROM_EMAIL}")
    
    print("=" * 60)
