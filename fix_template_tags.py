#!/usr/bin/env python
"""Fix Django template tags that span multiple lines."""

import re

file_path = r"c:\Users\Joseph James Banico\CSIT327-G7-RentMate\RentMate\templates\home_app\tenant-list.html"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all multi-line template tags by joining lines
# Pattern: finds {% if ... that continues on next line ... %}
patterns_to_fix = [
    # Status filters
    (r'{% if current_status==\'all\' or not\r?\n\s+current_status %}', 
     r"{% if current_status == 'all' or not current_status %}"),
    (r'{% if current_status==\'active\'\r?\n\s+%}', 
     r"{% if current_status == 'active' %}"),
    (r'{% if current_status==\'inactive\'\r?\n\s+%}', 
     r"{% if current_status == 'inactive' %}"),
    (r'{% if\r?\n\s+current_status==\'terminated\' %}', 
     r"{% if current_status == 'terminated' %}"),
    
    # Payment filters
    (r'{% if current_payment==\'all\' or not\r?\n\s+current_payment %}', 
     r"{% if current_payment == 'all' or not current_payment %}"),
    (r'{% if current_payment==\'paid\'\r?\n\s+%}', 
     r"{% if current_payment == 'paid' %}"),
    (r'{% if current_payment==\'pending\'\r?\n\s+%}', 
     r"{% if current_payment == 'pending' %}"),
    (r'{% if current_payment==\'overdue\'\r?\n\s+%}', 
     r"{% if current_payment == 'overdue' %}"),
    
    # Sort filters
    (r'{% if current_sort==\'name\' %}checked{%\r?\n\s+endif %}', 
     r"{% if current_sort == 'name' %}checked{% endif %}"),
    (r'{% if current_sort==\'unit\' %}checked{%\r?\n\s+endif %}', 
     r"{% if current_sort == 'unit' %}checked{% endif %}"),
    (r'{% if current_sort==\'start_date\'\r?\n\s+%}', 
     r"{% if current_sort == 'start_date' %}"),
    (r'{% if current_sort==\'end_date\'\r?\n\s+%}', 
     r"{% if current_sort == 'end_date' %}"),
    (r'{% if current_sort==\'rent\' %}checked{%\r?\n\s+endif %}', 
     r"{% if current_sort == 'rent' %}checked{% endif %}"),
    (r'{% if\r?\n\s+current_sort==\'payment_status\' %}', 
     r"{% if current_sort == 'payment_status' %}"),
    (r'{% if\r?\n\s+current_sort==\'rental_status\' %}', 
     r"{% if current_sort == 'rental_status' %}"),
]

for pattern, replacement in patterns_to_fix:
    content = re.sub(pattern, replacement, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all multi-line Django template tags!")
