from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time, timedelta
from .models import (
    Shift, AttendanceRecord, LeaveType, LeaveApplication, OvertimeRequest
)
from employees.models import Employee


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for Shift model"""
    
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Shift
        fields = [
            'id', 'name', 'shift_type', 'start_time', 'end_time',
            'break_duration', 'working_hours', 'employee_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['working_hours', 'created_at', 'updated_at']
    
    def get_employee_count(self, obj):
        """Get number of employees assigned to this shift"""
        # This would require a shift assignment model or field
        # For now, return 0 as placeholder
        return 0


class AttendanceRecordListSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord list view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date',
            'shift', 'shift_name', 'time_in', 'time_out', 'total_hours',
            'regular_hours', 'overtime_hours', 'status', 'is_late',
            'late_minutes', 'approved_by', 'approved_by_name', 'approved_at'
        ]


class AttendanceRecordDetailSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord detail view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date',
            'shift', 'shift_name', 'time_in', 'time_out', 'break_start',
            'break_end', 'total_hours', 'regular_hours', 'overtime_hours',
            'break_duration', 'status', 'is_late', 'late_minutes', 'notes',
            'check_in_location', 'check_out_location', 'ip_address',
            'approved_by', 'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_hours', 'regular_hours', 'overtime_hours', 'break_duration',
            'is_late', 'late_minutes', 'created_at', 'updated_at'
        ]


class AttendanceRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance records"""
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'employee', 'date', 'shift', 'time_in', 'time_out',
            'break_start', 'break_end', 'status', 'notes',
            'check_in_location', 'check_out_location'
        ]
    
    def validate(self, attrs):
        """Validate attendance record data"""
        employee = attrs.get('employee')
        date = attrs.get('date')
        time_in = attrs.get('time_in')
        time_out = attrs.get('time_out')
        break_start = attrs.get('break_start')
        break_end = attrs.get('break_end')
        
        # Check for duplicate attendance record
        if AttendanceRecord.objects.filter(employee=employee, date=date).exists():
            raise serializers.ValidationError("Attendance record for this employee and date already exists.")
        
        # Validate time_out is after time_in
        if time_in and time_out and time_out <= time_in:
            raise serializers.ValidationError("Time out must be after time in.")
        
        # Validate break times
        if break_start and break_end:
            if break_end <= break_start:
                raise serializers.ValidationError("Break end time must be after break start time.")
            
            if time_in and break_start < time_in:
                raise serializers.ValidationError("Break start time must be after time in.")
            
            if time_out and break_end > time_out:
                raise serializers.ValidationError("Break end time must be before time out.")
        
        return attrs


class CheckInSerializer(serializers.Serializer):
    """Serializer for employee check-in"""
    
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate check-in data"""
        user = self.context['request'].user
        today = timezone.now().date()
        
        # Check if already checked in today
        if AttendanceRecord.objects.filter(employee=user, date=today, time_in__isnull=False).exists():
            raise serializers.ValidationError("You have already checked in today.")
        
        return attrs


class CheckOutSerializer(serializers.Serializer):
    """Serializer for employee check-out"""
    
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate check-out data"""
        user = self.context['request'].user
        today = timezone.now().date()
        
        # Check if checked in today
        try:
            attendance = AttendanceRecord.objects.get(employee=user, date=today)
            if not attendance.time_in:
                raise serializers.ValidationError("You must check in before checking out.")
            if attendance.time_out:
                raise serializers.ValidationError("You have already checked out today.")
        except AttendanceRecord.DoesNotExist:
            raise serializers.ValidationError("No check-in record found for today.")
        
        return attrs


class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializer for LeaveType model"""
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'name', 'description', 'max_days_per_year', 'is_paid',
            'requires_approval', 'advance_notice_days', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveApplicationListSerializer(serializers.ModelSerializer):
    """Serializer for LeaveApplication list view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'leave_type', 'leave_type_name', 'start_date', 'end_date',
            'total_days', 'status', 'applied_at', 'approved_by',
            'approved_by_name', 'approved_at'
        ]


class LeaveApplicationDetailSerializer(serializers.ModelSerializer):
    """Serializer for LeaveApplication detail view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'leave_type', 'leave_type_name', 'start_date', 'end_date',
            'total_days', 'reason', 'status', 'applied_at',
            'approved_by', 'approved_by_name', 'approved_at',
            'rejection_reason', 'supporting_document', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_days', 'applied_at', 'approved_by', 'approved_at',
            'created_at', 'updated_at'
        ]


class LeaveApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating leave applications"""
    
    class Meta:
        model = LeaveApplication
        fields = [
            'leave_type', 'start_date', 'end_date', 'reason', 'supporting_document'
        ]
    
    def validate(self, attrs):
        """Validate leave application data"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        leave_type = attrs.get('leave_type')
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date.")
        
        # Check advance notice requirement
        if leave_type and start_date:
            advance_notice = leave_type.advance_notice_days
            notice_date = timezone.now().date() + timedelta(days=advance_notice)
            if start_date < notice_date:
                raise serializers.ValidationError(
                    f"This leave type requires {advance_notice} days advance notice."
                )
        
        # Check for overlapping leave applications
        employee = self.context['request'].user
        overlapping = LeaveApplication.objects.filter(
            employee=employee,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if overlapping.exists():
            raise serializers.ValidationError("You have overlapping leave applications.")
        
        return attrs
    
    def create(self, validated_data):
        """Create leave application"""
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)


class LeaveApprovalSerializer(serializers.Serializer):
    """Serializer for approving/rejecting leave applications"""
    
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate approval data"""
        action = attrs.get('action')
        reason = attrs.get('reason')
        
        if action == 'reject' and not reason:
            raise serializers.ValidationError("Reason is required when rejecting leave application.")
        
        return attrs


class OvertimeRequestListSerializer(serializers.ModelSerializer):
    """Serializer for OvertimeRequest list view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = OvertimeRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date',
            'start_time', 'end_time', 'hours_requested', 'status',
            'requested_at', 'approved_by', 'approved_by_name', 'approved_at'
        ]


class OvertimeRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for OvertimeRequest detail view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = OvertimeRequest
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'date',
            'start_time', 'end_time', 'hours_requested', 'reason', 'status',
            'requested_at', 'approved_by', 'approved_by_name', 'approved_at',
            'rejection_reason'
        ]
        read_only_fields = ['hours_requested', 'requested_at', 'approved_by', 'approved_at']


class OvertimeRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating overtime requests"""
    
    class Meta:
        model = OvertimeRequest
        fields = ['date', 'start_time', 'end_time', 'reason']
    
    def validate(self, attrs):
        """Validate overtime request data"""
        date = attrs.get('date')
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        # Validate time range
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")
        
        # Check for duplicate request
        employee = self.context['request'].user
        if OvertimeRequest.objects.filter(employee=employee, date=date).exists():
            raise serializers.ValidationError("Overtime request for this date already exists.")
        
        return attrs
    
    def create(self, validated_data):
        """Create overtime request"""
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    
    total_records = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    leave_days = serializers.IntegerField()
    
    attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    punctuality_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    total_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    regular_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    average_daily_hours = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Monthly breakdown
    monthly_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Status breakdown
    status_breakdown = serializers.ListField(
        child=serializers.DictField()
    )

