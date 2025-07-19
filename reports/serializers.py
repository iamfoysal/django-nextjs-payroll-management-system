from rest_framework import serializers
from decimal import Decimal
from datetime import datetime, date


class DateRangeSerializer(serializers.Serializer):
    """Base serializer for date range filters"""
    
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date.")
        
        return attrs


class ReportFilterSerializer(DateRangeSerializer):
    """Serializer for report filters"""
    
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of employee IDs to filter by"
    )
    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of department IDs to filter by"
    )
    export_format = serializers.ChoiceField(
        choices=['json', 'pdf', 'excel'],
        default='json',
        help_text="Export format for the report"
    )


class WorkingHoursReportSerializer(serializers.Serializer):
    """Serializer for working hours report"""
    
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    
    # Daily breakdown
    total_days = serializers.IntegerField()
    working_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    leave_days = serializers.IntegerField()
    
    # Hours breakdown
    total_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    regular_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    average_daily_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Rates
    attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    punctuality_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Daily details
    daily_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class OvertimeReportSerializer(serializers.Serializer):
    """Serializer for overtime report"""
    
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    
    # Overtime metrics
    total_overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    overtime_days = serializers.IntegerField()
    average_overtime_per_day = serializers.DecimalField(max_digits=6, decimal_places=2)
    overtime_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Breakdown by period
    weekly_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    monthly_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class LeaveReportSerializer(serializers.Serializer):
    """Serializer for leave report"""
    
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    
    # Leave balances
    annual_leave_balance = serializers.IntegerField()
    sick_leave_balance = serializers.IntegerField()
    casual_leave_balance = serializers.IntegerField()
    
    # Leave usage
    total_leaves_taken = serializers.IntegerField()
    annual_leaves_taken = serializers.IntegerField()
    sick_leaves_taken = serializers.IntegerField()
    casual_leaves_taken = serializers.IntegerField()
    
    # Leave breakdown by type
    leave_type_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Leave applications
    pending_applications = serializers.IntegerField()
    approved_applications = serializers.IntegerField()
    rejected_applications = serializers.IntegerField()
    
    # Monthly breakdown
    monthly_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class PayrollSummaryReportSerializer(serializers.Serializer):
    """Serializer for payroll summary report"""
    
    period_name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    # Employee counts
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    
    # Payroll totals
    total_gross_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_net_salary = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_bonuses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_overtime = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Averages
    average_gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Department breakdown
    department_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Status breakdown
    status_breakdown = serializers.ListField(
        child=serializers.DictField()
    )


class EmployeePerformanceReportSerializer(serializers.Serializer):
    """Serializer for employee performance insights"""
    
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    role = serializers.CharField()
    
    # Performance metrics
    attendance_reliability_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    punctuality_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    overtime_efficiency_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    leave_utilization_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    overall_performance_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Detailed metrics
    total_working_days = serializers.IntegerField()
    days_present = serializers.IntegerField()
    days_late = serializers.IntegerField()
    total_overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    leaves_taken = serializers.IntegerField()
    
    # Trends
    monthly_trends = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    
    # Recommendations
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class DepartmentAnalyticsSerializer(serializers.Serializer):
    """Serializer for department analytics"""
    
    department_id = serializers.IntegerField()
    department_name = serializers.CharField()
    
    # Employee metrics
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    
    # Attendance metrics
    average_attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_punctuality_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_overtime_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Payroll metrics
    total_payroll_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Leave metrics
    total_leaves_taken = serializers.IntegerField()
    average_leaves_per_employee = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Performance scores
    department_performance_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Employee breakdown
    employee_breakdown = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class CompanyAnalyticsSerializer(serializers.Serializer):
    """Serializer for company-wide analytics"""
    
    # Overview metrics
    total_employees = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_payroll_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Attendance overview
    company_attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    company_punctuality_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_overtime_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Leave overview
    total_leaves_taken = serializers.IntegerField()
    leave_approval_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Department comparison
    department_comparison = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Monthly trends
    monthly_trends = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Top performers
    top_performers = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Areas for improvement
    improvement_areas = serializers.ListField(
        child=serializers.DictField()
    )


class ReportExportSerializer(serializers.Serializer):
    """Serializer for report export requests"""
    
    report_type = serializers.ChoiceField(
        choices=[
            'working_hours',
            'overtime',
            'leave',
            'payroll_summary',
            'employee_performance',
            'department_analytics',
            'company_analytics'
        ]
    )
    export_format = serializers.ChoiceField(
        choices=['pdf', 'excel', 'csv']
    )
    filters = serializers.DictField(required=False)
    include_charts = serializers.BooleanField(default=True)
    email_to = serializers.EmailField(required=False)


class CustomReportSerializer(serializers.Serializer):
    """Serializer for custom report configuration"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # Data sources
    data_sources = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                'employees',
                'attendance',
                'payroll',
                'leaves',
                'departments'
            ]
        )
    )
    
    # Filters
    filters = serializers.DictField(required=False)
    
    # Grouping and aggregation
    group_by = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    aggregations = serializers.DictField(required=False)
    
    # Visualization
    chart_type = serializers.ChoiceField(
        choices=[
            'bar',
            'line',
            'pie',
            'table',
            'scatter'
        ],
        required=False
    )
    
    # Scheduling
    is_scheduled = serializers.BooleanField(default=False)
    schedule_frequency = serializers.ChoiceField(
        choices=[
            'daily',
            'weekly',
            'monthly',
            'quarterly'
        ],
        required=False
    )
    email_recipients = serializers.ListField(
        child=serializers.EmailField(),
        required=False
    )


class ReportMetadataSerializer(serializers.Serializer):
    """Serializer for report metadata"""
    
    report_id = serializers.CharField()
    report_name = serializers.CharField()
    generated_at = serializers.DateTimeField()
    generated_by = serializers.CharField()
    filters_applied = serializers.DictField()
    record_count = serializers.IntegerField()
    export_format = serializers.CharField()
    file_size = serializers.CharField(required=False)
    download_url = serializers.URLField(required=False)

