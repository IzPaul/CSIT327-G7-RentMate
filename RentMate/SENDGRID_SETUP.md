# SendGrid Email Integration

This document explains the SendGrid email integration in RentMate.

## Overview

RentMate now uses **SendGrid API** instead of SMTP to send emails. This provides:
- Better deliverability
- More reliable email sending
- Detailed analytics
- No need for SMTP credentials

## Configuration

### 1. SendGrid API Key

You need to obtain your own SendGrid API key:
1. Create a free account at [SendGrid.com](https://sendgrid.com)
2. Navigate to Settings → API Keys
3. Create a new API key with "Mail Send" permissions
4. Copy the API key (you'll only see it once!)

### 2. Environment Variables

For local development, add to your `.env` file:
```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

For production (Render), set the environment variable in your dashboard:
- Key: `SENDGRID_API_KEY`
- Value: `your_sendgrid_api_key_here`

### 3. Verified Sender Email

The following email must be verified in SendGrid:
```
rrentmate@gmail.com
```

**Important:** Make sure this email is verified in your SendGrid account:
1. Log in to SendGrid
2. Go to Settings → Sender Authentication
3. Verify `rrentmate@gmail.com` if not already verified

## How It Works

### Tenant Registration Flow

1. **Landlord creates tenant account** through the registration form
2. **System generates temporary password** automatically
3. **Email sent via SendGrid** to tenant's email with:
   - Email address (login username)
   - Temporary password
   - Login link
4. **Tenant receives email** and logs in
5. **First login prompts password change**

### Email Sending Implementation

The email is sent asynchronously using a background thread to avoid blocking the HTTP request:

```python
# EmailThread sends email in background
EmailThread(
    subject="Your Tenant Account - RentMate",
    message=email_message,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[tenant.email]
).start()
```

## Testing SendGrid

You can test the SendGrid integration using the provided test script:

```bash
cd RentMate
python test_sendgrid.py
```

This will:
- Load your SendGrid configuration
- Send a test email
- Display the response status

## Files Modified

1. **`RentMateProject/settings.py`**
   - Removed SMTP configuration
   - Added SendGrid API key configuration

2. **`apps/dashboard/views.py`**
   - Updated imports to use SendGrid
   - Modified `EmailThread` class to use SendGrid API
   - Updated email sending to use `DEFAULT_FROM_EMAIL`

3. **`requirements.txt`**
   - Already includes `sendgrid==6.11.0`

## Troubleshooting

### Email not sending

1. **Check SendGrid API key is valid**
   ```bash
   python test_sendgrid.py
   ```

2. **Verify sender email in SendGrid**
   - Log in to SendGrid dashboard
   - Check Sender Authentication settings

3. **Check application logs**
   - Look for "Email sent successfully" messages
   - Check for any SendGrid errors

### Common Errors

**Error: "The from email does not contain a valid address"**
- Solution: Verify `rrentmate@gmail.com` in SendGrid

**Error: "Unauthorized"**
- Solution: Check that `SENDGRID_API_KEY` is correct

**Error: "Forbidden"**
- Solution: Your SendGrid account may be restricted or API key doesn't have permission

## Production Deployment

When deploying to Render:

1. Set environment variable in Render dashboard:
   ```
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   ```

2. Ensure `rrentmate@gmail.com` is verified in SendGrid

3. Deploy the application

4. Test by creating a tenant account

## Code Example

Here's how the SendGrid email is sent:

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

# Create email
mail = Mail(
    from_email=settings.DEFAULT_FROM_EMAIL,
    to_emails=['tenant@example.com'],
    subject='Your Tenant Account - RentMate',
    plain_text_content='Your credentials...'
)

# Send via SendGrid
sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
response = sg.send(mail)
print(f"Status: {response.status_code}")
```

## Security Notes

- ✅ API key is stored in environment variables
- ✅ `.env` file is gitignored
- ✅ Production uses Render environment variables
- ⚠️ Never commit API keys to git
- ⚠️ Keep your SendGrid account secure

## Support

If you encounter issues with email delivery:
1. Check SendGrid dashboard for delivery status
2. Review application logs
3. Verify sender authentication
4. Contact SendGrid support if needed
