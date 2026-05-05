from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Employee, Payslip

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]

def _admin_required(request):
    return request.user.is_superuser or request.user.is_staff


@login_required
def employee_list(request):
    if not _admin_required(request):
        return redirect('payslip_list')
    employees = Employee.objects.all().order_by('name')
    return render(request, 'payroll_app/employee_list.html', {
        'employees': employees,
        'is_admin': _admin_required(request),
    })


@login_required
def employee_create(request):
    if not _admin_required(request):
        return redirect('payslip_list')

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        rate      = request.POST.get('rate', '').strip()
        allowance = request.POST.get('allowance', '').strip()

        errors = []
        if not name:      errors.append('Name is required.')
        if not id_number: errors.append('ID Number is required.')
        if not rate:      errors.append('Rate is required.')
        if Employee.objects.filter(id_number=id_number).exists():
            errors.append('An employee with that ID Number already exists.')
        
        if rate and float(rate) < 0:
            errors.append('Rate cannot be negative.')
        if allowance and float(allowance) < 0:
            errors.append('Allowance cannot be negative.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'payroll_app/employee_form.html', {
                'action': 'Create', 'form_data': request.POST,
                'is_admin': _admin_required(request),
            })

        Employee.objects.create(
            name=name, id_number=id_number, rate=float(rate),
            allowance=float(allowance) if allowance else None,
            overtime_pay=0.0,
        )

        # Auto-create Django login for this employee
        if not User.objects.filter(username=id_number).exists():
            User.objects.create_user(username=id_number, password='shemu123')

        messages.success(request, f'Employee {name} created. Login: {id_number} / shemu123')
        return redirect('employee_list')

    return render(request, 'payroll_app/employee_form.html', {
        'action': 'Create', 'form_data': {},
        'is_admin': _admin_required(request),
    })


@login_required
def employee_update(request, pk):
    if not _admin_required(request):
        return redirect('payslip_list')

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        rate      = request.POST.get('rate', '').strip()
        allowance = request.POST.get('allowance', '').strip()

        errors = []
        if not name:      errors.append('Name is required.')
        if not id_number: errors.append('ID Number is required.')
        if not rate:      errors.append('Rate is required.')
        if Employee.objects.filter(id_number=id_number).exclude(pk=pk).exists():
            errors.append('An employee with that ID Number already exists.')
        
        if rate and float(rate) < 0:
            errors.append('Rate cannot be negative.')
        if allowance and float(allowance) < 0:
            errors.append('Allowance cannot be negative.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'payroll_app/employee_form.html', {
                'action': 'Update', 'employee': employee, 'form_data': request.POST,
                'is_admin': _admin_required(request),
            })

        employee.name      = name
        employee.id_number = id_number
        employee.rate      = float(rate)
        employee.allowance = float(allowance) if allowance else None
        employee.save()
        messages.success(request, f'Employee {name} updated.')
        return redirect('employee_list')

    return render(request, 'payroll_app/employee_form.html', {
        'action': 'Update',
        'employee': employee,
        'is_admin': _admin_required(request),
        'form_data': {
            'name':      employee.name,
            'id_number': employee.id_number,
            'rate':      employee.rate,
            'allowance': employee.allowance if employee.allowance else '',
        },
    })


@login_required
def employee_delete(request, pk):
    if not _admin_required(request):
        return redirect('payslip_list')

    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f'Employee {name} deleted.')
    return redirect('employee_list')


@login_required
def employee_add_overtime(request, pk):
    if not _admin_required(request):
        return redirect('payslip_list')

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        hours_str = request.POST.get('overtime_hours', '').strip()

        if not hours_str:
            messages.error(request, 'Please enter the number of overtime hours.')
            return redirect('employee_list')

        try:
            hours = float(hours_str)
        except ValueError:
            messages.error(request, 'Overtime hours must be a number.')
            return redirect('employee_list')

        if hours < 0:
            messages.error(request, 'Overtime hours cannot be negative.')
            return redirect('employee_list')

        overtime_amount = (employee.rate / 160) * 1.5 * hours
        current = employee.overtime_pay or 0
        employee.overtime_pay = current + overtime_amount
        employee.save()

        messages.success(request,
            f'Added ₱{overtime_amount:.2f} overtime to {employee.name}. '
            f'Total: ₱{employee.overtime_pay:.2f}'
        )

    return redirect('employee_list')


@login_required
def payslip_list(request):
    is_admin = _admin_required(request)
    employees = Employee.objects.all().order_by('name')

    if is_admin:
        payslips = Payslip.objects.all().order_by('-pk')
    else:
        try:
            emp = Employee.objects.get(id_number=request.user.username)
            payslips = Payslip.objects.filter(id_number=emp).order_by('-pk')
        except Employee.DoesNotExist:
            payslips = Payslip.objects.none()
            messages.warning(request, 'Account not linked to an employee record.')

    error_msg = None

    if request.method == 'POST' and is_admin:
        payroll_for = request.POST.get('payroll_for', '')
        month       = request.POST.get('month', '')
        year        = request.POST.get('year', '').strip()
        cycle_str   = request.POST.get('cycle', '')

        if not all([payroll_for, month, year, cycle_str]):
            error_msg = 'All fields are required.'
        else:
            try:
                cycle = int(cycle_str)
                assert cycle in [1, 2]
            except (ValueError, AssertionError):
                error_msg = 'Cycle must be 1 or 2.'

        if not error_msg:
            date_range = '1-15' if cycle == 1 else '16-30'

            if payroll_for == 'all':
                target_employees = list(employees)
            else:
                try:
                    target_employees = [Employee.objects.get(id_number=payroll_for)]
                except Employee.DoesNotExist:
                    error_msg = 'Selected employee not found.'
                    target_employees = []

        if not error_msg:
            created_count = 0
            duplicate_ids = []

            for emp in target_employees:
                already_exists = Payslip.objects.filter(
                    id_number=emp, month=month,
                    year=year, pay_cycle=cycle,
                ).exists()

                if already_exists:
                    duplicate_ids.append(emp.id_number)
                    continue

                rate      = emp.rate
                allowance = emp.allowance or 0
                overtime  = emp.overtime_pay or 0
                cycle_rate = rate / 2

                if cycle == 1:
                    pag_ibig   = 100
                    philhealth = 0
                    sss        = 0
                    tax   = (cycle_rate + allowance + overtime - pag_ibig) * 0.20
                    gross = cycle_rate + allowance + overtime - pag_ibig
                    total = gross - tax
                else:
                    pag_ibig   = 0
                    philhealth = rate * 0.04
                    sss        = rate * 0.045
                    tax   = (cycle_rate + allowance + overtime - philhealth - sss) * 0.20
                    gross = cycle_rate + allowance + overtime - philhealth - sss
                    total = gross - tax

                Payslip.objects.create(
                    id_number=emp, month=month,
                    date_range=date_range, year=year,
                    pay_cycle=cycle, rate=rate,
                    earnings_allowance=allowance,
                    deductions_tax=round(tax, 2),
                    deductions_health=round(philhealth, 2),
                    pag_ibig=round(pag_ibig, 2),
                    sss=round(sss, 2),
                    overtime=round(overtime, 2),
                    total_pay=round(total, 2),
                )

                emp.resetOvertime()
                created_count += 1

            if created_count:
                messages.success(request, f'Generated {created_count} payslip(s) successfully.')
            if duplicate_ids:
                ids = ', '.join(duplicate_ids)
                error_msg = f'Payslip already exists for: {ids} in {month} {year} Cycle {cycle}'

    return render(request, 'payroll_app/payslip_list.html', {
        'employees': employees,
        'payslips':  Payslip.objects.all().order_by('-pk') if is_admin else payslips,
        'months':    MONTHS,
        'is_admin':  is_admin,
        'error_msg': error_msg,
    })


@login_required
def payslip_view(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    is_admin = _admin_required(request)

    if not is_admin:
        if payslip.id_number.id_number != request.user.username:
            messages.error(request, 'You do not have permission to view that payslip.')
            return redirect('payslip_list')

    return render(request, 'payroll_app/payslip_view.html', {
        'payslip': payslip,
        'is_admin': is_admin,
    })


def payslips_page(request):
    if request.method == 'POST':
        payroll_for = request.POST.get('payroll_for')
        month = request.POST.get('month')
        year = request.POST.get('year')
        cycle = int(request.POST.get('cycle'))
        
        employees = Employee.objects.all() if payroll_for == 'All' else Employee.objects.filter(id_number=payroll_for)
        
        for emp in employees:
            if Payslip.objects.filter(id_number=emp, month=month, year=year, pay_cycle=cycle).exists():
                messages.error(request, f"Payslip for {emp.name} in this cycle already exists.")
                continue

            rate = emp.rate
            cycle_rate = rate / 2
            allowance = emp.allowance if emp.allowance else 0
            overtime = emp.overtime_pay if emp.overtime_pay else 0

            pag_ibig = 0.0
            philhealth = 0.0
            sss = 0.0
            
            if cycle == 1:
                pag_ibig = 100.0
                taxable_income = cycle_rate + allowance + overtime - pag_ibig
            elif cycle == 2:
                philhealth = rate * 0.04
                sss = rate * 0.045
                taxable_income = cycle_rate + allowance + overtime - philhealth - sss
            
            tax = taxable_income * 0.2
            total_pay = taxable_income - tax

            Payslip.objects.create(
                id_number=emp,
                month=month,
                date_range="1-15" if cycle == 1 else "16-30",
                year=year,
                pay_cycle=cycle,
                rate=rate,
                earnings_allowance=allowance,
                deductions_tax=tax,
                deductions_health=philhealth,
                pag_ibig=pag_ibig,
                sss=sss,
                overtime=overtime,
                total_pay=total_pay
            )
            
            emp.resetOvertime()
            emp.save()
            
        return redirect('payslips')

    payslips = Payslip.objects.all()
    employees = Employee.objects.all()
    return render(request, 'payslips.html', {'payslips': payslips, 'employees': employees})