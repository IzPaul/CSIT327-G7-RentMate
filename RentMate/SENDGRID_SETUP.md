# SendGrid Email Configuration Guide

## Overview
This project has been configured to use SendGrid for sending emails instead of Gmail SMTP. This provides better deliverability, scalability, and security for production environments.

## Setup Instructions

### 1. Create a SendGrid Account
1. Go to [SendGrid](https://sendgrid.com/) and sign up for a free account (100 emails/day free tier)
2. Verify your email address

### 2. Verify a Sender Identity
Before you can send emails, you need to verify a sender identity:
1. Log in to SendGrid dashboard
2. Go to **Settings** → **Sender Authentication**
3. Choose one of the following options:
   - **Single Sender Verification** (easiest for development)
     - Click "Verify a Single Sender"
     - Enter your email address (e.g., `rrentmate@gmail.com`)
     - Complete the verification process
   - **Domain Authentication** (recommended for production)
     - Authenticate your own domain
     - Add DNS records as instructed

### 3. Create a SendGrid API Key
1. In SendGrid dashboard, go to **Settings** → **API Keys**
2. Click "Create API Key"
3. Give it a name (e.g., "RentMate Production")
4. Choose **Full Access** or **Restricted Access** (with Mail Send permissions)
5. Click "Create & View"
6. **IMPORTANT**: Copy the API key immediately (you won't be able to see it again!)

### 4. Configure Environment Variables

#### For Local Development:
Create a `.env` file in the `RentMate` directory:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# SendGrid Email Configuration
SENDGRID_API_KEY=SG.your-actual-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=your-verified-sender@example.com
```

#### For Render Deployment:
1. Go to your Render dashboard
2. Select your web service
3. Go to **Environment** tab
4. Add the following environment variables:
   - `SENDGRID_API_KEY` = `SG.your-actual-sendgrid-api-key-here`
   - `DEFAULT_FROM_EMAIL` = `your-verified-sender@example.com`

### 5. Test the Configuration

Test if emails are working correctly:

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message from RentMate.',
    'your-verified-sender@example.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

## Configuration Details

The following settings have been configured in `RentMateProject/settings.py`:

```python
# SendGrid Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literally the string 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'rrentmate@gmail.com')
```

## Important Notes

1. **API Key Security**: Never commit your SendGrid API key to version control
2. **Sender Verification**: The sender email must be verified in SendGrid
3. **Rate Limits**: Free tier allows 100 emails/day, upgrade if you need more
4. **Email Testing**: Test emails in development before deploying to production
5. **Monitoring**: Check SendGrid dashboard for email delivery statistics

## Troubleshooting

### Emails not sending:
1. Verify your SendGrid API key is correct
2. Ensure sender email is verified in SendGrid
3. Check Render logs for error messages
4. Verify environment variables are set correctly
5. Check SendGrid dashboard for error details

### Common Errors:
- `Authentication failed`: API key is incorrect or missing
- `Sender not verified`: Verify your sender identity in SendGrid
- `Rate limit exceeded`: Upgrade your SendGrid plan

## Support
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [SendGrid Support](https://support.sendgrid.com/)
