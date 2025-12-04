# How to Add Auto-Hide Messages to Templates

## Quick Fix (5 minutes)

To add auto-hide functionality to any page that shows Django messages, add this line **before the closing `</body>` tag**:

```html
{% include 'includes/message-auto-hide.html' %}
</body>
</html>
```

## Templates That Need This Fix

### Tenant Pages (3 files):
1. ✅ `templates/home_app_tenant/tenant-maintenance.html`
2. ✅ `templates/home_app_tenant/tenant-payment.html`
3. ✅ `templates/home_app_tenant/tenant-maintenance-list.html`

### Landlord Pages (6 files):
1. ✅ `templates/home_app/tenant-change-password.html`
2. ✅ `templates/home_app/tenant-account-register.html`
3. ✅ `templates/home_app/landlord-payments-list-update.html`
4. ✅ `templates/home_app/landlord-maintenance-update.html`
5. ✅ `templates/home_app/landlord-maintenance-list.html`
6. ✅ `templates/home_app/landlord-leases.html`

## What It Does

- **Auto-hides messages after 5 seconds** ⏱️
- **Adds a close button (×)** for manual dismissal ✖️
- **Smooth fade-out animation** ✨
- **Works with all message types** (success, error, warning, info)

## Example Before/After

### Before:
```html
    </div>
</body>
</html>
```

### After:
```html
    </div>
    {% include 'includes/message-auto-hide.html' %}
</body>
</html>
```

## Alternative: Add to Base Template

If you have a base template that all pages extend, you can add it **there once** instead of to each individual template.

## Files Created

- ✅ `templates/includes/message-auto-hide.html` - The reusable include file
- ✅ `static/js/message-handler.js` - Standalone JavaScript version (if you prefer script tags)
- ✅ `DJANGO_MESSAGES_FIX.md` - Full documentation

## Done!

That's it! Messages will now automatically hide and users can manually close them. 🎉
