from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal


class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    head_of_department = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='headed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """Role model for employee positions"""
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')
    description = models.TextField(blank=True, null=True)
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    overtime_rate_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('1.5'),
        validators=[MinValueValidator(Decimal('1.0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']
        unique_together = ['title', 'department']

    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Employee(AbstractUser):
    """Extended User model for employees"""
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
    ]
    
    SALARY_TYPE_CHOICES = [
        ('FIXED', 'Fixed Salary'),
        ('HOURLY', 'Hourly Rate'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Fix for Django User model conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='employee_set',
        related_query_name='employee',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='employee_set',
        related_query_name='employee',
    )
    
    # Personal Information
    employee_id = models.CharField(max_length=20, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='FULL_TIME')
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE_CHOICES, default='FIXED')
    
    # Salary Information
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Employment Dates
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    
    # Manager Relationship
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subordinates'
    )
    
    # Leave Balances
    annual_leave_balance = models.IntegerField(default=21)  # Days
    sick_leave_balance = models.IntegerField(default=10)   # Days
    casual_leave_balance = models.IntegerField(default=5)  # Days
    
    # Profile Picture
    profile_picture = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_current_salary(self):
        """Get current salary based on salary type"""
        if self.salary_type == 'FIXED':
            return self.base_salary or (self.role.base_salary if self.role else 0)
        else:
            return self.hourly_rate or (self.role.hourly_rate if self.role else 0)

    def get_overtime_rate(self):
        """Calculate overtime rate"""
        if self.salary_type == 'HOURLY':
            base_rate = self.get_current_salary()
            multiplier = self.role.overtime_rate_multiplier if self.role else Decimal('1.5')
            return base_rate * multiplier
        return Decimal('0')

    @property
    def is_employed(self):
        """Check if employee is currently employed"""
        return self.is_active and (self.termination_date is None)

    def save(self, *args, **kwargs):
        # Auto-generate employee ID if not provided
        if not self.employee_id:
            last_employee = Employee.objects.filter(
                employee_id__startswith='EMP'
            ).order_by('employee_id').last()
            
            if last_employee:
                last_id = int(last_employee.employee_id[3:])
                self.employee_id = f'EMP{last_id + 1:04d}'
            else:
                self.employee_id = 'EMP0001'
        
        # Set salary from role if not provided
        if self.role and not self.base_salary and not self.hourly_rate:
            if self.salary_type == 'FIXED':
                self.base_salary = self.role.base_salary
            else:
                self.hourly_rate = self.role.hourly_rate
        
        super().save(*args, **kwargs)


class EmployeeDocument(models.Model):
    """Model for storing employee documents"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('RESUME', 'Resume'),
        ('ID_PROOF', 'ID Proof'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('EDUCATION', 'Education Certificate'),
        ('EXPERIENCE', 'Experience Letter'),
        ('CONTRACT', 'Employment Contract'),
        ('OTHER', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='employee_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='uploaded_documents'
    )

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.title}"

