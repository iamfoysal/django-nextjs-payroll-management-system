from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from employees.models import Employee


class PayrollPeriod(models.Model):
    """Model for payroll periods (monthly, bi-weekly, etc.)"""
    
    PERIOD_TYPES = [
        ('WEEKLY', 'Weekly'),
        ('BI_WEEKLY', 'Bi-Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g., 'January 2024', 'Q1 2024'")
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES, default='MONTHLY')
    start_date = models.DateField()
    end_date = models.DateField()
    pay_date = models.DateField(help_text="Date when salaries will be paid")
    is_processed = models.BooleanField(default=False)
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ['start_date', 'end_date']
    
    def __str__(self):
        return self.name
    
    @property
    def total_days(self):
        """Calculate total days in the period"""
        return (self.end_date - self.start_date).days + 1


class TaxSlab(models.Model):
    """Model for income tax slabs"""
    
    name = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Leave blank for highest slab"
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tax rate as percentage"
    )
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['min_amount']
    
    def __str__(self):
        return f"{self.name} ({self.tax_rate}%)"


class DeductionType(models.Model):
    """Model for types of deductions (insurance, tax, etc.)"""
    
    CALCULATION_TYPES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage of Salary'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES)
    default_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Fixed amount or percentage value"
    )
    is_mandatory = models.BooleanField(default=False)
    is_taxable = models.BooleanField(default=True, help_text="Whether this deduction affects taxable income")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BonusType(models.Model):
    """Model for types of bonuses (performance, annual, etc.)"""
    
    CALCULATION_TYPES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage of Salary'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES)
    default_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Fixed amount or percentage value"
    )
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Payroll(models.Model):
    """Main payroll model for employee salary calculations"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CALCULATED', 'Calculated'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payrolls')
    
    # Salary components
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Attendance data
    total_working_days = models.IntegerField(default=0)
    days_worked = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    days_on_leave = models.IntegerField(default=0)
    regular_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Calculated amounts
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    calculated_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payroll_period__start_date', 'employee__employee_id']
        unique_together = ['employee', 'payroll_period']

    def calculate_salary(self):
        """Calculate salary for this payroll record"""
        from .utils import PayrollCalculator
        
        calculator = PayrollCalculator(self.employee, self.payroll_period)
        
        # Get attendance data
        attendance_data = calculator.get_attendance_data()
        
        # Update attendance fields
        self.total_working_days = calculator.calculate_working_days()
        self.days_worked = attendance_data['days_worked']
        self.days_absent = attendance_data['days_absent']
        self.days_on_leave = attendance_data['days_on_leave']
        self.regular_hours = attendance_data['regular_hours']
        self.overtime_hours = attendance_data['overtime_hours']
        
        # Set base salary and hourly rate from employee
        if not self.base_salary:
            self.base_salary = self.employee.base_salary or Decimal('0.00')
        if not self.hourly_rate:
            self.hourly_rate = self.employee.hourly_rate or Decimal('0.00')
        
        # Calculate salary components
        self.gross_salary = calculator.calculate_base_salary(attendance_data)
        self.overtime_amount = calculator.calculate_overtime_amount(attendance_data)
        
        # Save the record first so we can add deductions and bonuses
        if not self.pk:
            self.save()
        
        # Calculate bonuses and deductions
        self.total_bonuses = calculator.calculate_bonuses(self)
        self.total_deductions = calculator.calculate_deductions(self, self.gross_salary)
        
        # Calculate taxable income (gross + overtime + taxable bonuses - non-taxable deductions)
        taxable_income = self.gross_salary + self.overtime_amount
        
        # Add taxable bonuses
        for bonus in self.bonuses.all():
            if bonus.bonus_type.is_taxable:
                taxable_income += bonus.amount
        
        # Subtract non-taxable deductions
        for deduction in self.deductions.all():
            if not deduction.deduction_type.is_taxable:
                taxable_income -= deduction.amount
        
        # Calculate tax
        self.tax_amount = calculator.calculate_tax(taxable_income)
        
        # Calculate net salary
        self.net_salary = calculator.calculate_net_salary(
            self.gross_salary,
            self.overtime_amount,
            self.total_bonuses,
            self.total_deductions,
            self.tax_amount
        )
        
        # Update status and calculation timestamp
        self.status = 'CALCULATED'
        self.calculated_at = timezone.now()
        
        # Save the updated record
        self.save()
        
        return self
    
    def approve(self, approved_by):
        """Approve the payroll"""
        if self.status != 'CALCULATED':
            raise ValueError("Only calculated payrolls can be approved")
        
        self.status = 'APPROVED'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
    
    def mark_as_paid(self):
        """Mark payroll as paid"""
        if self.status != 'APPROVED':
            raise ValueError("Only approved payrolls can be marked as paid")
        
        self.status = 'PAID'
        self.paid_at = timezone.now()
        self.save()
    
    def generate_payslip(self, generated_by):
        """Generate pay slip for this payroll"""
        if self.status not in ['APPROVED', 'PAID']:
            raise ValueError("Only approved or paid payrolls can have pay slips generated")
        
        # Check if pay slip already exists
        existing_payslip = PaySlip.objects.filter(payroll=self).first()
        if existing_payslip:
            return existing_payslip
        
        # Generate slip number
        period_year = self.payroll_period.start_date.year
        period_month = self.payroll_period.start_date.month
        slip_count = PaySlip.objects.filter(
            payroll__payroll_period__start_date__year=period_year,
            payroll__payroll_period__start_date__month=period_month
        ).count() + 1
        
        slip_number = f"PS{period_year}{period_month:02d}{slip_count:04d}"
        
        # Create pay slip
        payslip = PaySlip.objects.create(
            payroll=self,
            slip_number=slip_number,
            generated_by=generated_by
        )
        
        return payslip
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.payroll_period.name}"


class PayrollDeduction(models.Model):
    """Model for individual deductions in a payroll"""
    
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='deductions')
    deduction_type = models.ForeignKey(DeductionType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['payroll', 'deduction_type']
    
    def __str__(self):
        return f"{self.payroll.employee.get_full_name()} - {self.deduction_type.name}: ${self.amount}"


class PayrollBonus(models.Model):
    """Model for individual bonuses in a payroll"""
    
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.ForeignKey(BonusType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['payroll', 'bonus_type']
    
    def __str__(self):
        return f"{self.payroll.employee.get_full_name()} - {self.bonus_type.name}: ${self.amount}"


class PayrollHistory(models.Model):
    """Model for tracking payroll changes and actions"""
    
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('CALCULATED', 'Calculated'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
        ('MODIFIED', 'Modified'),
    ]
    
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    previous_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.payroll} - {self.action} by {self.performed_by.get_full_name()}"


class PaySlip(models.Model):
    """Model for pay slips/salary slips"""
    
    payroll = models.OneToOneField(Payroll, on_delete=models.CASCADE, related_name='payslip')
    slip_number = models.CharField(max_length=50, unique=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True)
    emailed_to = models.EmailField(null=True, blank=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Pay Slip {self.slip_number} - {self.payroll.employee.get_full_name()}"

