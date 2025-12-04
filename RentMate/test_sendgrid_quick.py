"""
Quick test to verify SendGrid email sending with API key set directly
"""
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def test_sendgrid():
    """Test SendGrid with a simple email"""
    
    # IMPORTANT: Replace 'test@example.com' with YOUR actual email address!
    recipient_email = input("Enter your email address to test: ").strip()
    
    if not recipient_email or '@' not in recipient_email:
        print("❌ Invalid email address!")
        return
    
    print(f"\n📧 Sending test email to: {recipient_email}")
    print("⚠️  Check your spam folder if you don't see it in inbox!")
    
    # Create HTML email message
    message = Mail(
        from_email='rrentmate@gmail.com',  # Your SendGrid sender
        to_emails=recipient_email,
        subject='RentMate - SendGrid Test Email',
        html_content='''
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #3498db;">SendGrid Test Email</h2>
                <p>This is a test email from RentMate using SendGrid API.</p>
                <p>If you received this, SendGrid is working correctly! ✅</p>
                <hr>
                <p style="color: #777; font-size: 12px;">Sent via SendGrid API</p>
            </body>
        </html>
        '''
    )
    
    try:
        # Initialize SendGrid client
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        
        # Send the email
        response = sg.send(message)
        
        # Print response
        print("\n✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body.decode() if response.body else 'Empty'}")
        
        if response.status_code == 202:
            print("\n✨ Success! Email accepted by SendGrid.")
            print("📬 Check your email (including spam folder)")
        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
        
    except Exception as e:
        print(f"\n❌ Error sending email:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        # Check for common errors
        if "Unauthorized" in str(e):
            print("\n💡 Fix: Your API key may be invalid or expired")
        elif "does not contain a valid address" in str(e):
            print("\n💡 Fix: Your sender email (rrentmate@gmail.com) is not verified in SendGrid")
            print("   1. Go to https://app.sendgrid.com/settings/sender_auth")
            print("   2. Verify rrentmate@gmail.com as a sender")
        elif "Forbidden" in str(e):
            print("\n💡 Fix: Your SendGrid account may have restrictions")

if __name__ == "__main__":
    print("=" * 70)
    print("SendGrid Email Test - RentMate")
    print("=" * 70)
    test_sendgrid()
    print("=" * 70)
