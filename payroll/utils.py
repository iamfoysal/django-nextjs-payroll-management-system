from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from .models import TaxSlab, DeductionType, BonusType
from attendance.models import AttendanceRecord, LeaveApplication


class PayrollCalculator:
    """Utility class for payroll calculations"""
    
    def __init__(self, employee, payroll_period):
        self.employee = employee
        self.payroll_period = payroll_period
        self.calculation_date = timezone.now().date()
    
    def calculate_working_days(self):
        """Calculate total working days in the payroll period"""
        total_days = (self.payroll_period.end_date - self.payroll_period.start_date).days + 1
        
        # For simplicity, assume 5 working days per week (Monday to Friday)
        # In a real system, you might have a more complex calendar system
        working_days = 0
        current_date = self.payroll_period.start_date
        
        while current_date <= self.payroll_period.end_date:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def get_attendance_data(self):
        """Get attendance data for the employee in the payroll period"""
        attendance_records = AttendanceRecord.objects.filter(
            employee=self.employee,
            date__gte=self.payroll_period.start_date,
            date__lte=self.payroll_period.end_date
        )
        
        # Calculate attendance metrics
        total_records = attendance_records.count()
        present_days = attendance_records.filter(status='PRESENT').count()
        absent_days = attendance_records.filter(status='ABSENT').count()
        leave_days = attendance_records.filter(status='LEAVE').count()
        
        # Calculate hours
        total_hours = attendance_records.aggregate(
            total=Sum('total_hours')
        )['total'] or Decimal('0.00')
        
        regular_hours = attendance_records.aggregate(
            total=Sum('regular_hours')
        )['total'] or Decimal('0.00')
        
        overtime_hours = attendance_records.aggregate(
            total=Sum('overtime_hours')
        )['total'] or Decimal('0.00')
        
        return {
            'days_worked': present_days,
            'days_absent': absent_days,
            'days_on_leave': leave_days,
            'regular_hours': regular_hours,
            'overtime_hours': overtime_hours,
            'total_hours': total_hours
        }
    
    def calculate_base_salary(self, attendance_data):
        """Calculate base salary based on employment type and attendance"""
        if self.employee.salary_type == 'FIXED':
            # Fixed salary - calculate based on days worked
            total_working_days = self.calculate_working_days()
            days_worked = attendance_data['days_worked']
            
            if total_working_days > 0:
                daily_rate = self.employee.base_salary / total_working_days
                base_salary = daily_rate * days_worked
            else:
                base_salary = self.employee.base_salary
        
        elif self.employee.salary_type == 'HOURLY':
            # Hourly salary - calculate based on hours worked
            regular_hours = attendance_data['regular_hours']
            hourly_rate = self.employee.hourly_rate or Decimal('0.00')
            base_salary = regular_hours * hourly_rate
        
        else:
            base_salary = Decimal('0.00')
        
        return base_salary.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_overtime_amount(self, attendance_data):
        """Calculate overtime amount"""
        overtime_hours = attendance_data['overtime_hours']
        
        if overtime_hours <= 0:
            return Decimal('0.00')
        
        # Get overtime rate (default to 1.5x regular rate)
        if self.employee.salary_type == 'HOURLY':
            base_rate = self.employee.hourly_rate or Decimal('0.00')
        else:
            # For fixed salary, calculate hourly rate
            total_working_days = self.calculate_working_days()
            hours_per_day = Decimal('8.00')  # Standard 8 hours per day
            total_hours = total_working_days * hours_per_day
            
            if total_hours > 0:
                base_rate = self.employee.base_salary / total_hours
            else:
                base_rate = Decimal('0.00')
        
        # Overtime rate is typically 1.5x the regular rate
        overtime_rate = base_rate * Decimal('1.5')
        overtime_amount = overtime_hours * overtime_rate
        
        return overtime_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_bonuses(self, payroll):
        """Calculate total bonuses for the payroll"""
        total_bonuses = Decimal('0.00')
        
        # Get bonuses from PayrollBonus records
        bonus_records = payroll.bonuses.all()
        for bonus in bonus_records:
            total_bonuses += bonus.amount
        
        # Add automatic bonuses based on performance, attendance, etc.
        # This is where you could add business logic for automatic bonuses
        
        return total_bonuses.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_deductions(self, payroll, gross_salary):
        """Calculate total deductions for the payroll"""
        total_deductions = Decimal('0.00')
        
        # Get deductions from PayrollDeduction records
        deduction_records = payroll.deductions.all()
        for deduction in deduction_records:
            total_deductions += deduction.amount
        
        # Add mandatory deductions
        mandatory_deductions = DeductionType.objects.filter(
            is_mandatory=True,
            is_active=True
        )
        
        for deduction_type in mandatory_deductions:
            # Check if this deduction is already added manually
            if not deduction_records.filter(deduction_type=deduction_type).exists():
                amount = self.calculate_deduction_amount(deduction_type, gross_salary)
                if amount > 0:
                    # Create the deduction record
                    from .models import PayrollDeduction
                    PayrollDeduction.objects.create(
                        payroll=payroll,
                        deduction_type=deduction_type,
                        amount=amount,
                        description=f"Automatic {deduction_type.name}"
                    )
                    total_deductions += amount
        
        return total_deductions.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_deduction_amount(self, deduction_type, gross_salary):
        """Calculate amount for a specific deduction type"""
        if deduction_type.calculation_type == 'FIXED':
            return deduction_type.default_amount or Decimal('0.00')
        
        elif deduction_type.calculation_type == 'PERCENTAGE':
            percentage = deduction_type.default_amount or Decimal('0.00')
            return (gross_salary * percentage / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        return Decimal('0.00')
    
    def calculate_tax(self, taxable_income):
        """Calculate income tax based on tax slabs"""
        if taxable_income <= 0:
            return Decimal('0.00')
        
        # Get active tax slabs for current date
        from django.db import models
        tax_slabs = TaxSlab.objects.filter(
            is_active=True,
            effective_from__lte=self.calculation_date
        ).filter(
            models.Q(effective_to__isnull=True) | 
            models.Q(effective_to__gte=self.calculation_date)
        ).order_by('min_amount')
        
        total_tax = Decimal('0.00')
        remaining_income = taxable_income
        
        for slab in tax_slabs:
            if remaining_income <= 0:
                break
            
            # Determine the taxable amount for this slab
            slab_min = slab.min_amount
            slab_max = slab.max_amount
            
            if slab_max and remaining_income > slab_max:
                taxable_in_slab = slab_max - slab_min
            else:
                taxable_in_slab = remaining_income - slab_min
            
            if taxable_in_slab > 0:
                slab_tax = taxable_in_slab * (slab.tax_rate / 100)
                total_tax += slab_tax
                remaining_income -= taxable_in_slab
        
        return total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_net_salary(self, gross_salary, overtime_amount, total_bonuses, 
                           total_deductions, tax_amount):
        """Calculate final net salary"""
        net_salary = (
            gross_salary + 
            overtime_amount + 
            total_bonuses - 
            total_deductions - 
            tax_amount
        )
        
        # Ensure net salary is not negative
        return max(net_salary, Decimal('0.00')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def get_leave_balance(self):
        """Get employee's leave balance"""
        current_year = timezone.now().year
        
        # Calculate used leave days for current year
        used_leaves = LeaveApplication.objects.filter(
            employee=self.employee,
            status='APPROVED',
            start_date__year=current_year
        ).aggregate(
            total_days=Sum('total_days')
        )['total_days'] or 0
        
        return {
            'annual_leave_balance': self.employee.annual_leave_balance,
            'sick_leave_balance': self.employee.sick_leave_balance,
            'casual_leave_balance': self.employee.casual_leave_balance,
            'used_leaves_this_year': used_leaves
        }


class PayrollReportGenerator:
    """Utility class for generating payroll reports"""
    
    @staticmethod
    def generate_payroll_summary(payroll_period):
        """Generate payroll summary for a period"""
        from .models import Payroll
        
        payrolls = Payroll.objects.filter(payroll_period=payroll_period)
        
        summary = {
            'period': payroll_period.name,
            'start_date': payroll_period.start_date,
            'end_date': payroll_period.end_date,
            'total_employees': payrolls.count(),
            'total_gross_salary': payrolls.aggregate(
                total=Sum('gross_salary')
            )['total'] or Decimal('0.00'),
            'total_net_salary': payrolls.aggregate(
                total=Sum('net_salary')
            )['total'] or Decimal('0.00'),
            'total_deductions': payrolls.aggregate(
                total=Sum('total_deductions')
            )['total'] or Decimal('0.00'),
            'total_bonuses': payrolls.aggregate(
                total=Sum('total_bonuses')
            )['total'] or Decimal('0.00'),
            'total_tax': payrolls.aggregate(
                total=Sum('tax_amount')
            )['total'] or Decimal('0.00'),
            'status_breakdown': list(
                payrolls.values('status').annotate(
                    count=Count('id')
                )
            )
        }
        
        return summary
    
    @staticmethod
    def generate_employee_payroll_history(employee, start_date=None, end_date=None):
        """Generate payroll history for an employee"""
        from .models import Payroll
        
        payrolls = Payroll.objects.filter(employee=employee)
        
        if start_date:
            payrolls = payrolls.filter(payroll_period__start_date__gte=start_date)
        if end_date:
            payrolls = payrolls.filter(payroll_period__end_date__lte=end_date)
        
        payrolls = payrolls.order_by('-payroll_period__start_date')
        
        history = []
        for payroll in payrolls:
            history.append({
                'period': payroll.payroll_period.name,
                'start_date': payroll.payroll_period.start_date,
                'end_date': payroll.payroll_period.end_date,
                'gross_salary': payroll.gross_salary,
                'net_salary': payroll.net_salary,
                'total_deductions': payroll.total_deductions,
                'total_bonuses': payroll.total_bonuses,
                'tax_amount': payroll.tax_amount,
                'status': payroll.status,
                'paid_at': payroll.paid_at
            })
        
        return {
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.get_full_name(),
                'department': employee.department.name if employee.department else None
            },
            'payroll_history': history,
            'summary': {
                'total_periods': len(history),
                'total_gross': sum(p['gross_salary'] for p in history),
                'total_net': sum(p['net_salary'] for p in history),
                'average_gross': sum(p['gross_salary'] for p in history) / len(history) if history else 0,
                'average_net': sum(p['net_salary'] for p in history) / len(history) if history else 0
            }
        }


def round_currency(amount):
    """Round currency amount to 2 decimal places"""
    if amount is None:
        return Decimal('0.00')
    return Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_currency(amount, currency_symbol='$'):
    """Format currency amount for display"""
    if amount is None:
        amount = Decimal('0.00')
    return f"{currency_symbol}{amount:,.2f}"


def calculate_annual_salary(monthly_salary):
    """Calculate annual salary from monthly salary"""
    return monthly_salary * 12


def calculate_monthly_salary(annual_salary):
    """Calculate monthly salary from annual salary"""
    return annual_salary / 12


def get_pay_frequency_multiplier(frequency):
    """Get multiplier for different pay frequencies"""
    multipliers = {
        'WEEKLY': 52,
        'BI_WEEKLY': 26,
        'MONTHLY': 12,
        'QUARTERLY': 4,
        'ANNUALLY': 1
    }
    return multipliers.get(frequency, 12)  # Default to monthly

