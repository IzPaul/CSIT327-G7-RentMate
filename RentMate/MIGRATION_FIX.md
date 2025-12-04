# Migration Fix for Render Deployment

## Problem
The migration `0002_monthlybilling` is trying to create a table that already exists in production.

Error: `django.db.utils.ProgrammingError: relation "dashboard_monthlybilling" already exists`

## Solution: Fake the Migration

### Update Render Build Command:

Replace your current build command with:

```bash
pip install -r requirements.txt && python manage.py migrate dashboard 0002_alter_maintenancerequest_maintenance_type --fake && python manage.py migrate dashboard 0002_monthlybilling --fake && python manage.py migrate
```

**OR** if you want to fake just the problematic migration:

```bash
pip install -r requirements.txt && python manage.py migrate dashboard 0002_monthlybilling --fake && python manage.py migrate
```

### What this does:
- Marks the migration as applied WITHOUT actually running the SQL
- Allows Django to proceed with subsequent migrations
- Doesn't affect the existing table structure

---

## Alternative: Delete Duplicate Migration (Clean Solution)

If the `dashboard_monthlybilling` table was already created by a previous migration that was later deleted:

### Steps:

1. **Check if there's an older migration** that created this table
2. **Keep only ONE migration** that creates the MonthlyBilling model
3. **Delete the duplicate** `0002_monthlybilling.py`
4. **Recreate a fresh migration**:
   ```bash
   python manage.py makemigrations
   ```

---

## Quick Fix for Current Deployment:

Run this command manually in Render's shell:

```bash
python manage.py migrate dashboard 0002_monthlybilling --fake
python manage.py migrate
```

Then your next deployment will work fine.

---

## Prevention:

To avoid this in the future:
1. Always pull latest migrations before creating new ones
2. Use `python manage.py migrate --fake-initial` for first deployment
3. Keep migration files in version control

---

## Current Migration State:

```
0001_initial.py  (creates base models)
0002_alter_maintenancerequest_maintenance_type.py (updates maintenance)
0002_monthlybilling.py (creates MonthlyBilling) ← PROBLEMATIC
0003_merge_20251205_0210.py (merges the two 0002 migrations)
```

The merge migration (0003) was created to resolve the conflict, but the table already exists in production.
