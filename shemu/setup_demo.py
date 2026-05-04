"""
setup_demo.py — Run once to create demo accounts.

Usage (Command Prompt):
    python manage.py shell < setup_demo.py

Usage (PowerShell):
    Get-Content setup_demo.py | python manage.py shell

Creates:
    - admin / admin123  (superuser — full access)
    - 150726 / emp123   (employee — own payslips only)
"""
from django.contrib.auth.models import User
from payroll_app.models import Employee

# ── Admin superuser ──────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shemu.com', 'admin123')
    print('✅ Created admin user (admin / admin123)')
else:
    print('ℹ️  admin user already exists')

# ── Sample employee record ───────────────────────────────────────────
emp_id = '150726'
if not Employee.objects.filter(id_number=emp_id).exists():
    Employee.objects.create(
        name='Luis Cajucom',
        id_number=emp_id,
        rate=25000,
        allowance=None,
        overtime_pay=0,
    )
    print(f'✅ Created employee record: {emp_id}')
else:
    print(f'ℹ️  Employee {emp_id} already exists')

# ── Matching Django login for that employee ──────────────────────────
# IMPORTANT: username must equal id_number — this links login to employee record
if not User.objects.filter(username=emp_id).exists():
    User.objects.create_user(emp_id, password='emp123')
    print(f'✅ Created employee login ({emp_id} / emp123)')
else:
    print(f'ℹ️  Login for {emp_id} already exists')

print('\nDone! Login accounts:')
print('  Admin:    admin / admin123')
print('  Employee: 150726 / emp123')
