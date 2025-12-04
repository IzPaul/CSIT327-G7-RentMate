# Django Messages Persistence Issue - Fix Documentation

## Problem
Success messages from one action (e.g., "Tenant updated successfully!") are appearing on unrelated pages (Maintenance Request, Payment pages). This happens because Django messages persist in the session until they are properly consumed/displayed.

## Root Cause
Django's message framework stores messages in the session, and they should be automatically consumed when rendered in a template. However, if a user navigates to a different page before the message is displayed, or if the message template tag is present on multiple pages, old messages can appear on wrong pages.

## Solution Options

### Option 1: Auto-Hide Messages with JavaScript (Implemented)
The file `static/js/message-handler.js` has been created to:
- Auto-hide messages after 5 seconds
- Add a close button to manually dismiss messages
- Fade out smoothly

**To use:** Add this script to any template that displays messages:
```html
<script src="{% static 'js/message-handler.js' %}"></script>
```

### Option 2: Use Message Tags for Better Filtering
Modify views to use specific message tags:
```python
from django.contrib import messages

# In tenant_update_view
messages.success(request, 'Tenant updated successfully!', extra_tags='tenant-update')

# In maintenance view
messages.success(request, 'Maintenance request submitted successfully!', extra_tags='maintenance')
```

Then filter in templates:
```html
{% for message in messages %}
    {% if 'tenant' in message.tags %}
        {# Only show on tenant pages #}
    {% endif %}
{% endfor %}
```

### Option 3: Clear Messages Before Redirect (Recommended)
Ensure messages are cleared appropriately:
```python
from django.contrib import messages as django_messages

# Clear all messages before setting a new one
storage = django_messages.get_messages(request)
for _ in storage:
    pass  # This consumes the messages

# Then set the new message
messages.success(request, 'New message here')
```

### Option 4: Use Session-Based Flags Instead
For critical actions, use session flags:
```python
# Set flag
request.session['tenant_updated'] = True
return redirect('tenant_list')

# In view
if request.session.pop('tenant_updated', False):
    messages.success(request, 'Tenant updated successfully!')
```

## Recommended Implementation
1. Add the message-handler.js script to base templates
2. Update success messages to be more specific:
   - "Maintenance request submitted!" instead of "Tenant updated!"
   - "Payment submitted!" instead of "Tenant updated!"
3. Ensure redirects go to the correct pages

## Files to Update
- `templates/home_app_tenant/tenant-maintenance.html` - Add message handler script
- `templates/home_app_tenant/tenant-payment.html` - Add message handler script
- `apps/dashboard/views.py` - Update message texts to be action-specific
