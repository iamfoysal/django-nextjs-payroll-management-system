from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date
from .models import (
    PayrollPeriod, TaxSlab, DeductionType, BonusType, Payroll,
    PayrollDeduction, PayrollBonus, PayrollHistory, PaySlip
)
from employees.models import Employee


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Serializer for PayrollPeriod model"""
    
    total_days = serializers.ReadOnlyField()
    payroll_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'name', 'period_type', 'start_date', 'end_date', 'pay_date',
            'total_days', 'is_processed', 'is_finalized', 'payroll_count',
            'total_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_payroll_count(self, obj):
        """Get number of payrolls in this period"""
        return obj.payrolls.count()
    
    def get_total_amount(self, obj):
        """Get total payroll amount for this period"""
        return obj.payrolls.aggregate(
            total=serializers.models.Sum('net_salary')
        )['total'] or Decimal('0.00')


class TaxSlabSerializer(serializers.ModelSerializer):
    """Serializer for TaxSlab model"""
    
    class Meta:
        model = TaxSlab
        fields = [
            'id', 'name', 'min_amount', 'max_amount', 'tax_rate',
            'is_active', 'effective_from', 'effective_to', 'created_at'
        ]
        read_only_fields = ['created_at']


class DeductionTypeSerializer(serializers.ModelSerializer):
    """Serializer for DeductionType model"""
    
    class Meta:
        model = DeductionType
        fields = [
            'id', 'name', 'description', 'calculation_type', 'default_amount',
            'is_mandatory', 'is_taxable', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BonusTypeSerializer(serializers.ModelSerializer):
    """Serializer for BonusType model"""
    
    class Meta:
        model = BonusType
        fields = [
            'id', 'name', 'description', 'calculation_type', 'default_amount',
            'is_taxable', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PayrollDeductionSerializer(serializers.ModelSerializer):
    """Serializer for PayrollDeduction model"""
    
    deduction_type_name = serializers.CharField(source='deduction_type.name', read_only=True)
    
    class Meta:
        model = PayrollDeduction
        fields = [
            'id', 'deduction_type', 'deduction_type_name', 'amount',
            'description', 'created_at'
        ]
        read_only_fields = ['created_at']


class PayrollBonusSerializer(serializers.ModelSerializer):
    """Serializer for PayrollBonus model"""
    
    bonus_type_name = serializers.CharField(source='bonus_type.name', read_only=True)
    
    class Meta:
        model = PayrollBonus
        fields = [
            'id', 'bonus_type', 'bonus_type_name', 'amount',
            'description', 'created_at'
        ]
        read_only_fields = ['created_at']


class PayrollListSerializer(serializers.ModelSerializer):
    """Serializer for Payroll list view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'payroll_period', 'period_name', 'gross_salary', 'net_salary',
            'status', 'calculated_at', 'approved_by', 'approved_by_name',
            'approved_at', 'paid_at'
        ]


class PayrollDetailSerializer(serializers.ModelSerializer):
    """Serializer for Payroll detail view"""
    
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    deductions = PayrollDeductionSerializer(many=True, read_only=True)
    bonuses = PayrollBonusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'payroll_period', 'period_name', 'base_salary', 'hourly_rate',
            'total_working_days', 'days_worked', 'days_absent', 'days_on_leave',
            'regular_hours', 'overtime_hours', 'gross_salary', 'overtime_amount',
            'total_bonuses', 'total_deductions', 'tax_amount', 'net_salary',
            'status', 'calculated_at', 'approved_by', 'approved_by_name',
            'approved_at', 'paid_at', 'notes', 'deductions', 'bonuses',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'gross_salary', 'overtime_amount', 'total_bonuses', 'total_deductions',
            'tax_amount', 'net_salary', 'calculated_at', 'approved_by',
            'approved_at', 'paid_at', 'created_at', 'updated_at'
        ]


class PayrollCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payroll records"""
    
    deductions = PayrollDeductionSerializer(many=True, required=False)
    bonuses = PayrollBonusSerializer(many=True, required=False)
    
    class Meta:
        model = Payroll
        fields = [
            'employee', 'payroll_period', 'notes', 'deductions', 'bonuses'
        ]
    
    def validate(self, attrs):
        """Validate payroll creation data"""
        employee = attrs.get('employee')
        payroll_period = attrs.get('payroll_period')
        
        # Check if payroll already exists for this employee and period
        if Payroll.objects.filter(employee=employee, payroll_period=payroll_period).exists():
            raise serializers.ValidationError(
                "Payroll already exists for this employee and period."
            )
        
        # Check if payroll period is finalized
        if payroll_period.is_finalized:
            raise serializers.ValidationError(
                "Cannot create payroll for a finalized period."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create payroll with deductions and bonuses"""
        deductions_data = validated_data.pop('deductions', [])
        bonuses_data = validated_data.pop('bonuses', [])
        
        # Create payroll
        payroll = Payroll.objects.create(**validated_data)
        
        # Create deductions
        for deduction_data in deductions_data:
            PayrollDeduction.objects.create(payroll=payroll, **deduction_data)
        
        # Create bonuses
        for bonus_data in bonuses_data:
            PayrollBonus.objects.create(payroll=payroll, **bonus_data)
        
        # Calculate salary
        payroll.calculate_salary()
        
        return payroll


class PayrollCalculationSerializer(serializers.Serializer):
    """Serializer for payroll calculation parameters"""
    
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of employee IDs to calculate payroll for. If empty, calculates for all employees."
    )
    payroll_period_id = serializers.IntegerField(
        help_text="ID of the payroll period to calculate for"
    )
    recalculate = serializers.BooleanField(
        default=False,
        help_text="Whether to recalculate existing payrolls"
    )
    
    def validate_payroll_period_id(self, value):
        """Validate payroll period exists"""
        try:
            PayrollPeriod.objects.get(id=value)
        except PayrollPeriod.DoesNotExist:
            raise serializers.ValidationError("Payroll period not found.")
        return value


class PayrollApprovalSerializer(serializers.Serializer):
    """Serializer for payroll approval"""
    
    payroll_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of payroll IDs to approve"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Optional approval notes"
    )


class PayrollHistorySerializer(serializers.ModelSerializer):
    """Serializer for PayrollHistory model"""
    
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = PayrollHistory
        fields = [
            'id', 'action', 'performed_by', 'performed_by_name',
            'timestamp', 'notes', 'previous_values', 'new_values'
        ]
        read_only_fields = ['timestamp']


class PaySlipSerializer(serializers.ModelSerializer):
    """Serializer for PaySlip model"""
    
    employee_name = serializers.CharField(source='payroll.employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='payroll.employee.employee_id', read_only=True)
    period_name = serializers.CharField(source='payroll.payroll_period.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = PaySlip
        fields = [
            'id', 'payroll', 'employee_name', 'employee_id', 'period_name',
            'slip_number', 'generated_at', 'generated_by', 'generated_by_name',
            'pdf_file', 'emailed_to', 'emailed_at'
        ]
        read_only_fields = ['slip_number', 'generated_at']


class PayrollStatsSerializer(serializers.Serializer):
    """Serializer for payroll statistics"""
    
    total_payrolls = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Status breakdown
    draft_count = serializers.IntegerField()
    calculated_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    
    # Department breakdown
    department_breakdown = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Monthly trends
    monthly_trends = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Top earners
    top_earners = serializers.ListField(
        child=serializers.DictField()
    )


class SalaryCalculationSerializer(serializers.Serializer):
    """Serializer for salary calculation preview"""
    
    employee_id = serializers.IntegerField()
    payroll_period_id = serializers.IntegerField()
    
    # Optional overrides
    base_salary_override = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    hourly_rate_override = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False
    )
    bonus_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=Decimal('0.00')
    )
    deduction_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=Decimal('0.00')
    )
    
    def validate_employee_id(self, value):
        """Validate employee exists"""
        try:
            Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")
        return value
    
    def validate_payroll_period_id(self, value):
        """Validate payroll period exists"""
        try:
            PayrollPeriod.objects.get(id=value)
        except PayrollPeriod.DoesNotExist:
            raise serializers.ValidationError("Payroll period not found.")
        return value


class SalaryCalculationResultSerializer(serializers.Serializer):
    """Serializer for salary calculation results"""
    
    employee_name = serializers.CharField()
    employee_id = serializers.CharField()
    period_name = serializers.CharField()
    
    # Basic salary components
    base_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    hourly_rate = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # Hours and attendance
    total_working_days = serializers.IntegerField()
    days_worked = serializers.IntegerField()
    days_absent = serializers.IntegerField()
    days_on_leave = serializers.IntegerField()
    regular_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Salary calculations
    gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    overtime_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_bonuses = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Breakdown details
    bonus_breakdown = serializers.ListField(child=serializers.DictField())
    deduction_breakdown = serializers.ListField(child=serializers.DictField())
    tax_breakdown = serializers.ListField(child=serializers.DictField())

