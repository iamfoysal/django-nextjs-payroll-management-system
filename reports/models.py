from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date
from employees.models import Employee, Department
from payroll.models import PayrollPeriod


class ReportTemplate(models.Model):
    """Model for defining report templates"""
    
    REPORT_TYPE_CHOICES = [
        ('ATTENDANCE', 'Attendance Report'),
        ('PAYROLL', 'Payroll Report'),
        ('OVERTIME', 'Overtime Report'),
        ('LEAVE', 'Leave Report'),
        ('EMPLOYEE', 'Employee Report'),
        ('DEPARTMENT', 'Department Report'),
        ('PERFORMANCE', 'Performance Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=12, choices=REPORT_TYPE_CHOICES)
    default_format = models.CharField(max_length=5, choices=FORMAT_CHOICES, default='PDF')
    
    # Template configuration
    fields_to_include = models.JSONField(default=list)  # List of fields to include
    filters = models.JSONField(default=dict)  # Default filters
    grouping = models.JSONField(default=dict)  # Grouping configuration
    sorting = models.JSONField(default=dict)  # Sorting configuration
    
    # Access control
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    allowed_roles = models.JSONField(default=list)  # List of roles that can access this template
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class GeneratedReport(models.Model):
    """Model for tracking generated reports"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    name = models.CharField(max_length=200)
    
    # Report parameters
    date_from = models.DateField()
    date_to = models.DateField()
    departments = models.ManyToManyField(Department, blank=True)
    employees = models.ManyToManyField(Employee, blank=True, related_name='reports')
    additional_filters = models.JSONField(default=dict)
    
    # Generation details
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    format = models.CharField(max_length=5, choices=ReportTemplate.FORMAT_CHOICES)
    
    # File and results
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # Size in bytes
    total_records = models.IntegerField(default=0)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    # Access tracking
    download_count = models.IntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.name} - {self.status}"

    @property
    def processing_time(self):
        """Calculate processing time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def mark_as_processing(self):
        """Mark report as processing"""
        self.status = 'PROCESSING'
        self.started_at = timezone.now()
        self.save()

    def mark_as_completed(self, file_path=None, total_records=0):
        """Mark report as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if file_path:
            self.file_path = file_path
        self.total_records = total_records
        self.save()

    def mark_as_failed(self, error_message):
        """Mark report as failed"""
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()


class AttendanceAnalytics(models.Model):
    """Model for storing attendance analytics data"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_analytics')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='attendance_analytics')
    
    # Time period
    year = models.IntegerField()
    month = models.IntegerField()
    
    # Attendance metrics
    total_working_days = models.IntegerField(default=0)
    days_present = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    days_on_leave = models.IntegerField(default=0)
    days_late = models.IntegerField(default=0)
    
    # Time metrics
    total_hours_worked = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    regular_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    average_daily_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Performance metrics
    attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    punctuality_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', 'employee__employee_id']
        unique_together = ['employee', 'year', 'month']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.year}/{self.month:02d}"

    def calculate_metrics(self):
        """Calculate all attendance metrics for the period"""
        from attendance.models import AttendanceRecord
        from calendar import monthrange
        
        # Get the date range for the month
        start_date = date(self.year, self.month, 1)
        _, last_day = monthrange(self.year, self.month)
        end_date = date(self.year, self.month, last_day)
        
        # Get attendance records for the period
        records = AttendanceRecord.objects.filter(
            employee=self.employee,
            date__range=[start_date, end_date]
        )
        
        # Calculate basic metrics
        self.total_working_days = records.count()
        self.days_present = records.filter(status='PRESENT').count()
        self.days_absent = records.filter(status='ABSENT').count()
        self.days_on_leave = records.filter(status='LEAVE').count()
        self.days_late = records.filter(is_late=True).count()
        
        # Calculate time metrics
        self.total_hours_worked = sum(record.total_hours for record in records)
        self.regular_hours = sum(record.regular_hours for record in records)
        self.overtime_hours = sum(record.overtime_hours for record in records)
        
        if self.days_present > 0:
            self.average_daily_hours = self.total_hours_worked / self.days_present
        
        # Calculate performance metrics
        if self.total_working_days > 0:
            self.attendance_percentage = (self.days_present / self.total_working_days) * 100
            
            if self.days_present > 0:
                self.punctuality_percentage = ((self.days_present - self.days_late) / self.days_present) * 100
        
        self.save()


class PayrollAnalytics(models.Model):
    """Model for storing payroll analytics data"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_analytics')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='payroll_analytics')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='analytics')
    
    # Salary components
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    overtime_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Performance metrics
    cost_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    overtime_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payroll_period__start_date', 'employee__employee_id']
        unique_together = ['employee', 'payroll_period']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.payroll_period.name}"


class DepartmentAnalytics(models.Model):
    """Model for storing department-level analytics"""
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_analytics')
    
    # Time period
    year = models.IntegerField()
    month = models.IntegerField()
    
    # Employee metrics
    total_employees = models.IntegerField(default=0)
    active_employees = models.IntegerField(default=0)
    new_hires = models.IntegerField(default=0)
    terminations = models.IntegerField(default=0)
    
    # Attendance metrics
    average_attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    average_punctuality_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_overtime_hours = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Payroll metrics
    total_payroll_cost = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_overtime_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Leave metrics
    total_leave_days = models.IntegerField(default=0)
    average_leave_per_employee = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', 'department__name']
        unique_together = ['department', 'year', 'month']

    def __str__(self):
        return f"{self.department.name} - {self.year}/{self.month:02d}"


class PerformanceMetrics(models.Model):
    """Model for storing employee performance metrics"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Time period
    year = models.IntegerField()
    quarter = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    
    # Attendance performance
    attendance_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    punctuality_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    # Productivity metrics
    overtime_efficiency = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Ratio of overtime hours to regular productivity"
    )
    leave_to_productivity_ratio = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Impact of leave on productivity"
    )
    
    # Overall performance
    overall_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))]
    )
    
    # Performance grade
    GRADE_CHOICES = [
        ('A+', 'Excellent (90-100)'),
        ('A', 'Very Good (80-89)'),
        ('B+', 'Good (70-79)'),
        ('B', 'Satisfactory (60-69)'),
        ('C', 'Needs Improvement (50-59)'),
        ('D', 'Poor (Below 50)'),
    ]
    
    performance_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    
    # Comments and notes
    manager_comments = models.TextField(blank=True)
    improvement_areas = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    
    # Review details
    reviewed_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reviewed_performances'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-quarter', 'employee__employee_id']
        unique_together = ['employee', 'year', 'quarter']

    def __str__(self):
        return f"{self.employee.get_full_name()} - Q{self.quarter} {self.year} ({self.performance_grade})"

    def calculate_overall_score(self):
        """Calculate overall performance score"""
        # Weighted average of different metrics
        weights = {
            'attendance': 0.3,
            'punctuality': 0.2,
            'overtime_efficiency': 0.25,
            'leave_productivity': 0.25
        }
        
        self.overall_score = (
            self.attendance_score * weights['attendance'] +
            self.punctuality_score * weights['punctuality'] +
            self.overtime_efficiency * weights['overtime_efficiency'] +
            self.leave_to_productivity_ratio * weights['leave_productivity']
        )
        
        # Assign grade based on score
        if self.overall_score >= 90:
            self.performance_grade = 'A+'
        elif self.overall_score >= 80:
            self.performance_grade = 'A'
        elif self.overall_score >= 70:
            self.performance_grade = 'B+'
        elif self.overall_score >= 60:
            self.performance_grade = 'B'
        elif self.overall_score >= 50:
            self.performance_grade = 'C'
        else:
            self.performance_grade = 'D'
        
        self.save()


class ReportSchedule(models.Model):
    """Model for scheduling automatic report generation"""
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    
    # Recipients
    email_recipients = models.JSONField(default=list)  # List of email addresses
    employee_recipients = models.ManyToManyField(Employee, blank=True, related_name='scheduled_reports')
    
    # Schedule settings
    is_active = models.BooleanField(default=True)
    next_run_date = models.DateTimeField()
    last_run_date = models.DateTimeField(null=True, blank=True)
    
    # Creation details
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.frequency})"

