# Table Alignment Fix Guide for RentMate

## Problem
The table headers and data cells are misaligned because:
1. The header `<table>` and body `<table>` are separate
2. No fixed column widths are specified
3. This causes columns to have different widths

## Solution
Add `<colgroup>` with fixed widths to BOTH header and body tables.

---

## Fix 1: Tenant List (tenant-list.html)

### Location: Lines 128-173

### Replace with:

```html
        <!-- Tenant Lists Section -->
        <div class="tenants-table-container">
            <table class="tenants-table" style="table-layout: fixed; width: 100%;">
                <colgroup>
                    <col style="width: 12%;">  <!-- Full Name -->
                    <col style="width: 15%;">  <!-- Email -->
                    <col style="width: 11%;">  <!-- Phone -->
                    <col style="width: 7%;">   <!-- Unit -->
                    <col style="width: 9%;">   <!-- Start Date -->
                    <col style="width: 9%;">   <!-- End Date -->
                    <col style="width: 10%;">  <!-- Monthly Rent -->
                    <col style="width: 11%;">  <!-- Payment Status -->
                    <col style="width: 10%;">  <!-- Rental Status -->
                    <col style="width: 6%;">   <!-- Action -->
                </colgroup>
                <thead>
                    <tr>
                        <th>Full Name</th>
                        <th>Email</th>
                        <th>Phone Number</th>
                        <th>Unit</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th>Monthly Rent</th>
                        <th>Payment Status</th>
                        <th>Rental Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
            </table>
            <div class="tenants-table-wrapper">
                <table class="tenants-table" style="table-layout: fixed; width: 100%;">
                    <colgroup>
                        <col style="width: 12%;">  <!-- Full Name -->
                        <col style="width: 15%;">  <!-- Email -->
                        <col style="width: 11%;">  <!-- Phone -->
                        <col style="width: 7%;">   <!-- Unit -->
                        <col style="width: 9%;">   <!-- Start Date -->
                        <col style="width: 9%;">   <!-- End Date -->
                        <col style="width: 10%;">  <!-- Monthly Rent -->
                        <col style="width: 11%;">  <!-- Payment Status -->
                        <col style="width: 10%;">  <!-- Rental Status -->
                        <col style="width: 6%;">   <!-- Action -->
                    </colgroup>
                    <tbody>
                        {% for tenant in tenants %}
                            <tr class="clickable-row" data-href="{% url 'landlord_tenant_profile' tenant.id %}">
                                <td>{{ tenant.first_name }} {{ tenant.last_name }}</td>
                                <td>{{ tenant.email }}</td>
                                <td>{{ tenant.phone_number }}</td>
                                <td>{{ tenant.unit }}</td>
                                <td>{{ tenant.lease_start|date:"m-d-Y"|default:"-" }}</td>
                                <td>{{ tenant.lease_end|date:"m-d-Y"|default:"-" }}</td>
                                <td>P{{ tenant.rent }}</td>
                                <td class="status {{ tenant.payment_status|lower }}">{{ tenant.payment_status }}</td>
                                <td class="status {{ tenant.status|lower }}">{{ tenant.status }}</td>
                                <td class="actions-cell">
                                    <a href="{% url 'delete_tenant' tenant.id %}" class="btn-delete"
                                    onclick="return confirm('Are you sure you want to delete this tenant?')">Delete</a>
                                </td>
                            </tr>
                        {% empty %}
                            <tr>
                                <td colspan="10" class="no-data">No tenants found.</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
```

### Important Changes:
1. ✅ Added `table-layout: fixed; width: 100%;` to BOTH tables
2. ✅ Added identical `<colgroup>` to BOTH tables (header and body)
3. ✅ Fixed closing tag from `</div>` to `</table>` on line 172
4. ✅ Changed colspan from 9 to 10 in empty state (10 columns total)

---

That's the fix! The key points are:
- BOTH tables need the same column widths
- Use `table-layout: fixed`
- The percentages must add up to 100%
- Header and body tables must have IDENTICAL <colgroup> definitions

