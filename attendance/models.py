from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, time, timedelta
from employees.models import Employee


class Shift(models.Model):
    """Model for defining work shifts"""
    
    SHIFT_TYPE_CHOICES = [
        ('DAY', 'Day Shift'),
        ('NIGHT', 'Night Shift'),
        ('FLEXIBLE', 'Flexible'),
    ]
    
    name = models.CharField(max_length=50)
    shift_type = models.CharField(max_length=10, choices=SHIFT_TYPE_CHOICES, default='DAY')
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.DurationField(default=timedelta(hours=1))  # Default 1 hour break
    working_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('24.0'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

    def save(self, *args, **kwargs):
        # Calculate working hours automatically
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)
            
            # Handle overnight shifts
            if self.end_time < self.start_time:
                end_datetime += timedelta(days=1)
            
            total_duration = end_datetime - start_datetime
            break_duration = self.break_duration or timedelta(0)
            working_duration = total_duration - break_duration
            
            self.working_hours = Decimal(str(working_duration.total_seconds() / 3600))
        
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    """Model for daily attendance records"""
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('HOLIDAY', 'Holiday'),
        ('LEAVE', 'On Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Time tracking
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    
    # Calculated fields
    total_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    regular_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    overtime_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    break_duration = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Status and notes
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    is_late = models.BooleanField(default=False)
    late_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    # Location tracking (optional)
    check_in_location = models.CharField(max_length=200, blank=True)
    check_out_location = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_attendance'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_in']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.status})"

    def calculate_hours(self):
        """Calculate total hours, regular hours, and overtime"""
        if not self.time_in or not self.time_out:
            return
        
        # Calculate total working time
        total_time = self.time_out - self.time_in
        
        # Subtract break time
        if self.break_start and self.break_end:
            break_time = self.break_end - self.break_start
            self.break_duration = Decimal(str(break_time.total_seconds() / 3600))
            total_time -= break_time
        
        self.total_hours = Decimal(str(total_time.total_seconds() / 3600))
        
        # Calculate regular and overtime hours
        if self.shift:
            expected_hours = self.shift.working_hours
        else:
            expected_hours = Decimal('8.0')  # Default 8 hours
        
        if self.total_hours <= expected_hours:
            self.regular_hours = self.total_hours
            self.overtime_hours = Decimal('0.00')
        else:
            self.regular_hours = expected_hours
            self.overtime_hours = self.total_hours - expected_hours
        
        # Check if late
        if self.shift and self.time_in:
            expected_time = datetime.combine(self.date, self.shift.start_time)
            expected_time = timezone.make_aware(expected_time)
            
            if self.time_in > expected_time:
                self.is_late = True
                late_duration = self.time_in - expected_time
                self.late_minutes = int(late_duration.total_seconds() / 60)
            else:
                self.is_late = False
                self.late_minutes = 0

    def save(self, *args, **kwargs):
        self.calculate_hours()
        super().save(*args, **kwargs)


class LeaveType(models.Model):
    """Model for different types of leaves"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    max_days_per_year = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(365)]
    )
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    advance_notice_days = models.IntegerField(default=1)  # Minimum days notice required
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    """Model for leave applications"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Approval workflow
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Supporting documents
    supporting_document = models.FileField(
        upload_to='leave_documents/', 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date cannot be after end date.")
            
            # Calculate total days
            self.total_days = (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def approve(self, approved_by):
        """Approve the leave application"""
        self.status = 'APPROVED'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()

    def reject(self, rejected_by, reason):
        """Reject the leave application"""
        self.status = 'REJECTED'
        self.approved_by = rejected_by
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()


class OvertimeRequest(models.Model):
    """Model for overtime requests"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_requests')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours_requested = models.DecimalField(max_digits=4, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # Approval
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_overtime'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_at']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.hours_requested}h)"

    def save(self, *args, **kwargs):
        # Calculate hours requested
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)
            
            if self.end_time < self.start_time:
                end_datetime += timedelta(days=1)
            
            duration = end_datetime - start_datetime
            self.hours_requested = Decimal(str(duration.total_seconds() / 3600))
        
        super().save(*args, **kwargs)

