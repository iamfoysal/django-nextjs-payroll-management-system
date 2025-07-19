from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Employee, Department, Role, EmployeeDocument


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    
    employee_count = serializers.SerializerMethodField()
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'head_of_department', 'head_name',
            'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        """Get the number of employees in this department"""
        return obj.employee_set.filter(is_active=True).count()
    
    def get_head_name(self, obj):
        """Get the name of the department head"""
        if obj.head_of_department:
            return obj.head_of_department.get_full_name()
        return None


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'title', 'department', 'department_name', 'description',
            'base_salary', 'hourly_rate', 'overtime_rate_multiplier',
            'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        """Get the number of employees with this role"""
        return obj.employee_set.filter(is_active=True).count()


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer for Employee list view (minimal fields)"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_title = serializers.CharField(source='role.title', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    current_salary = serializers.DecimalField(source='get_current_salary', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'username', 'email', 'full_name',
            'first_name', 'last_name', 'phone_number', 'department',
            'department_name', 'role', 'role_title', 'employment_type',
            'salary_type', 'current_salary', 'manager', 'manager_name',
            'hire_date', 'is_active', 'is_employed'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer for Employee detail view (all fields)"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_title = serializers.CharField(source='role.title', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    current_salary = serializers.DecimalField(source='get_current_salary', max_digits=10, decimal_places=2, read_only=True)
    overtime_rate = serializers.DecimalField(source='get_overtime_rate', max_digits=8, decimal_places=2, read_only=True)
    subordinates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'username', 'email', 'full_name',
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'department_name', 'role', 'role_title',
            'employment_type', 'salary_type', 'base_salary', 'hourly_rate',
            'current_salary', 'overtime_rate', 'hire_date', 'termination_date',
            'manager', 'manager_name', 'subordinates_count',
            'annual_leave_balance', 'sick_leave_balance', 'casual_leave_balance',
            'profile_picture', 'is_active', 'is_employed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at', 'is_employed']
    
    def get_subordinates_count(self, obj):
        """Get the number of subordinates"""
        return obj.subordinates.filter(is_active=True).count()


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new employees"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'role', 'employment_type', 'salary_type',
            'base_salary', 'hourly_rate', 'hire_date', 'manager',
            'annual_leave_balance', 'sick_leave_balance', 'casual_leave_balance'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password and password confirmation do not match.")
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness"""
        if Employee.objects.filter(username=value).exists():
            raise serializers.ValidationError("An employee with this username already exists.")
        return value
    
    def create(self, validated_data):
        """Create new employee with hashed password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        employee = Employee.objects.create_user(
            password=password,
            **validated_data
        )
        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employee information"""
    
    class Meta:
        model = Employee
        fields = [
            'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'role', 'employment_type', 'salary_type',
            'base_salary', 'hourly_rate', 'manager',
            'annual_leave_balance', 'sick_leave_balance', 'casual_leave_balance',
            'profile_picture', 'is_active'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness (excluding current instance)"""
        if Employee.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value


class EmployeePasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing employee password"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return attrs
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Employee documents"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'employee', 'employee_name', 'document_type', 'title',
            'file', 'file_size', 'uploaded_at', 'uploaded_by', 'uploaded_by_name'
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by']
    
    def get_file_size(self, obj):
        """Get file size in human readable format"""
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return None


class EmployeeStatsSerializer(serializers.Serializer):
    """Serializer for employee statistics"""
    
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    inactive_employees = serializers.IntegerField()
    departments_count = serializers.IntegerField()
    roles_count = serializers.IntegerField()
    new_hires_this_month = serializers.IntegerField()
    terminations_this_month = serializers.IntegerField()
    
    # Department breakdown
    department_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Employment type breakdown
    employment_type_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Salary type breakdown
    salary_type_breakdown = serializers.ListField(
        child=serializers.DictField()
    )

