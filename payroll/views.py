from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    PayrollPeriod, TaxSlab, DeductionType, BonusType, Payroll,
    PayrollDeduction, PayrollBonus, PayrollHistory, PaySlip
)
from .serializers import (
    PayrollPeriodSerializer, TaxSlabSerializer, DeductionTypeSerializer,
    BonusTypeSerializer, PayrollListSerializer, PayrollDetailSerializer,
    PayrollCreateSerializer, PayrollCalculationSerializer, PayrollApprovalSerializer,
    PayrollHistorySerializer, PaySlipSerializer, PayrollStatsSerializer,
    SalaryCalculationSerializer, SalaryCalculationResultSerializer
)
from employees.models import Employee
from employees.permissions import CanManagePayroll, IsHROrManager
from attendance.models import AttendanceRecord


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for PayrollPeriod CRUD operations"""
    
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'pay_date', 'created_at']
    ordering = ['-start_date']
    filterset_fields = ['period_type', 'is_processed', 'is_finalized']
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Mark payroll period as processed"""
        period = self.get_object()
        
        if period.is_processed:
            return Response(
                {'error': 'Payroll period is already processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        period.is_processed = True
        period.save()
        
        return Response({'message': 'Payroll period marked as processed.'})
    
    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize payroll period (no more changes allowed)"""
        period = self.get_object()
        
        if period.is_finalized:
            return Response(
                {'error': 'Payroll period is already finalized.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not period.is_processed:
            return Response(
                {'error': 'Payroll period must be processed before finalizing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        period.is_finalized = True
        period.save()
        
        return Response({'message': 'Payroll period finalized successfully.'})
    
    @action(detail=True, methods=['get'])
    def payrolls(self, request, pk=None):
        """Get all payrolls for this period"""
        period = self.get_object()
        payrolls = period.payrolls.all()
        
        # Apply pagination
        page = self.paginate_queryset(payrolls)
        if page is not None:
            serializer = PayrollListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayrollListSerializer(payrolls, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active payroll period"""
        today = timezone.now().date()
        
        try:
            period = PayrollPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            ).first()
            
            if period:
                serializer = PayrollPeriodSerializer(period)
                return Response(serializer.data)
            else:
                return Response(
                    {'message': 'No active payroll period found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': f'Error finding current period: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaxSlabViewSet(viewsets.ModelViewSet):
    """ViewSet for TaxSlab CRUD operations"""
    
    queryset = TaxSlab.objects.all()
    serializer_class = TaxSlabSerializer
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['min_amount', 'tax_rate', 'effective_from']
    ordering = ['min_amount']
    filterset_fields = ['is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active tax slabs for current date"""
        today = timezone.now().date()
        
        slabs = TaxSlab.objects.filter(
            is_active=True,
            effective_from__lte=today
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=today)
        ).order_by('min_amount')
        
        serializer = TaxSlabSerializer(slabs, many=True)
        return Response(serializer.data)


class DeductionTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for DeductionType CRUD operations"""
    
    queryset = DeductionType.objects.all()
    serializer_class = DeductionTypeSerializer
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'default_amount', 'created_at']
    ordering = ['name']
    filterset_fields = ['calculation_type', 'is_mandatory', 'is_taxable', 'is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active deduction types"""
        deductions = DeductionType.objects.filter(is_active=True)
        serializer = DeductionTypeSerializer(deductions, many=True)
        return Response(serializer.data)


class BonusTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for BonusType CRUD operations"""
    
    queryset = BonusType.objects.all()
    serializer_class = BonusTypeSerializer
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'default_amount', 'created_at']
    ordering = ['name']
    filterset_fields = ['calculation_type', 'is_taxable', 'is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active bonus types"""
        bonuses = BonusType.objects.filter(is_active=True)
        serializer = BonusTypeSerializer(bonuses, many=True)
        return Response(serializer.data)


class PayrollViewSet(viewsets.ModelViewSet):
    """ViewSet for Payroll CRUD operations"""
    
    queryset = Payroll.objects.select_related(
        'employee', 'payroll_period', 'approved_by'
    ).prefetch_related('deductions', 'bonuses').all()
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'payroll_period__name'
    ]
    ordering_fields = ['created_at', 'calculated_at', 'net_salary']
    ordering = ['-created_at']
    filterset_fields = ['employee', 'payroll_period', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PayrollListSerializer
        elif self.action == 'create':
            return PayrollCreateSerializer
        else:
            return PayrollDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own payroll
        if not self.request.user.is_staff and not self.request.user.groups.filter(
            name__in=['HR', 'Finance']
        ).exists():
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def calculate_bulk(self, request):
        """Calculate payroll for multiple employees"""
        serializer = PayrollCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            employee_ids = serializer.validated_data.get('employee_ids', [])
            payroll_period_id = serializer.validated_data['payroll_period_id']
            recalculate = serializer.validated_data.get('recalculate', False)
            
            try:
                payroll_period = PayrollPeriod.objects.get(id=payroll_period_id)
                
                # Get employees to calculate for
                if employee_ids:
                    employees = Employee.objects.filter(id__in=employee_ids, is_active=True)
                else:
                    employees = Employee.objects.filter(is_active=True)
                
                results = []
                errors = []
                
                for employee in employees:
                    try:
                        # Check if payroll already exists
                        payroll, created = Payroll.objects.get_or_create(
                            employee=employee,
                            payroll_period=payroll_period,
                            defaults={'status': 'DRAFT'}
                        )
                        
                        if not created and not recalculate:
                            errors.append(f"Payroll already exists for {employee.get_full_name()}")
                            continue
                        
                        # Calculate salary
                        payroll.calculate_salary()
                        
                        results.append({
                            'employee_id': employee.id,
                            'employee_name': employee.get_full_name(),
                            'payroll_id': payroll.id,
                            'net_salary': payroll.net_salary,
                            'status': 'calculated'
                        })
                        
                    except Exception as e:
                        errors.append(f"Error calculating for {employee.get_full_name()}: {str(e)}")
                
                return Response({
                    'message': f'Calculated payroll for {len(results)} employees.',
                    'results': results,
                    'errors': errors
                })
                
            except PayrollPeriod.DoesNotExist:
                return Response(
                    {'error': 'Payroll period not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': f'Calculation failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def approve_bulk(self, request):
        """Approve multiple payrolls"""
        serializer = PayrollApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            payroll_ids = serializer.validated_data['payroll_ids']
            notes = serializer.validated_data.get('notes', '')
            
            try:
                payrolls = Payroll.objects.filter(
                    id__in=payroll_ids,
                    status='CALCULATED'
                )
                
                approved_count = 0
                for payroll in payrolls:
                    payroll.approve(request.user)
                    
                    # Add history record
                    PayrollHistory.objects.create(
                        payroll=payroll,
                        action='APPROVED',
                        performed_by=request.user,
                        notes=notes
                    )
                    
                    approved_count += 1
                
                return Response({
                    'message': f'Approved {approved_count} payrolls successfully.',
                    'approved_count': approved_count
                })
                
            except Exception as e:
                return Response(
                    {'error': f'Approval failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve individual payroll"""
        payroll = self.get_object()
        
        if payroll.status != 'CALCULATED':
            return Response(
                {'error': 'Only calculated payrolls can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll.approve(request.user)
        
        # Add history record
        PayrollHistory.objects.create(
            payroll=payroll,
            action='APPROVED',
            performed_by=request.user,
            notes=request.data.get('notes', '')
        )
        
        return Response({'message': 'Payroll approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payroll as paid"""
        payroll = self.get_object()
        
        if payroll.status != 'APPROVED':
            return Response(
                {'error': 'Only approved payrolls can be marked as paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll.mark_as_paid()
        
        # Add history record
        PayrollHistory.objects.create(
            payroll=payroll,
            action='PAID',
            performed_by=request.user,
            notes=request.data.get('notes', '')
        )
        
        return Response({'message': 'Payroll marked as paid successfully.'})
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate payroll"""
        payroll = self.get_object()
        
        if payroll.status in ['APPROVED', 'PAID']:
            return Response(
                {'error': 'Cannot recalculate approved or paid payrolls.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payroll.calculate_salary()
        
        # Add history record
        PayrollHistory.objects.create(
            payroll=payroll,
            action='CALCULATED',
            performed_by=request.user,
            notes='Payroll recalculated'
        )
        
        serializer = PayrollDetailSerializer(payroll)
        return Response({
            'message': 'Payroll recalculated successfully.',
            'payroll': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get payroll history"""
        payroll = self.get_object()
        history = payroll.history.all()
        serializer = PayrollHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_payrolls(self, request):
        """Get current user's payrolls"""
        payrolls = self.get_queryset().filter(employee=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(payrolls)
        if page is not None:
            serializer = PayrollListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PayrollListSerializer(payrolls, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate_preview(self, request):
        """Preview salary calculation without saving"""
        serializer = SalaryCalculationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                employee = Employee.objects.get(id=serializer.validated_data['employee_id'])
                payroll_period = PayrollPeriod.objects.get(
                    id=serializer.validated_data['payroll_period_id']
                )
                
                # Create temporary payroll object for calculation
                temp_payroll = Payroll(
                    employee=employee,
                    payroll_period=payroll_period
                )
                
                # Apply overrides if provided
                if 'base_salary_override' in serializer.validated_data:
                    temp_payroll.base_salary = serializer.validated_data['base_salary_override']
                if 'hourly_rate_override' in serializer.validated_data:
                    temp_payroll.hourly_rate = serializer.validated_data['hourly_rate_override']
                
                # Calculate without saving
                temp_payroll.calculate_salary()
                
                # Add bonus/deduction overrides
                bonus_amount = serializer.validated_data.get('bonus_amount', Decimal('0.00'))
                deduction_amount = serializer.validated_data.get('deduction_amount', Decimal('0.00'))
                
                temp_payroll.total_bonuses += bonus_amount
                temp_payroll.total_deductions += deduction_amount
                temp_payroll.net_salary = (
                    temp_payroll.gross_salary + 
                    temp_payroll.overtime_amount + 
                    temp_payroll.total_bonuses - 
                    temp_payroll.total_deductions - 
                    temp_payroll.tax_amount
                )
                
                # Prepare result data
                result_data = {
                    'employee_name': employee.get_full_name(),
                    'employee_id': employee.employee_id,
                    'period_name': payroll_period.name,
                    'base_salary': temp_payroll.base_salary,
                    'hourly_rate': temp_payroll.hourly_rate,
                    'total_working_days': temp_payroll.total_working_days,
                    'days_worked': temp_payroll.days_worked,
                    'days_absent': temp_payroll.days_absent,
                    'days_on_leave': temp_payroll.days_on_leave,
                    'regular_hours': temp_payroll.regular_hours,
                    'overtime_hours': temp_payroll.overtime_hours,
                    'gross_salary': temp_payroll.gross_salary,
                    'overtime_amount': temp_payroll.overtime_amount,
                    'total_bonuses': temp_payroll.total_bonuses,
                    'total_deductions': temp_payroll.total_deductions,
                    'tax_amount': temp_payroll.tax_amount,
                    'net_salary': temp_payroll.net_salary,
                    'bonus_breakdown': [{'name': 'Additional Bonus', 'amount': bonus_amount}] if bonus_amount > 0 else [],
                    'deduction_breakdown': [{'name': 'Additional Deduction', 'amount': deduction_amount}] if deduction_amount > 0 else [],
                    'tax_breakdown': [{'name': 'Income Tax', 'amount': temp_payroll.tax_amount}]
                }
                
                result_serializer = SalaryCalculationResultSerializer(result_data)
                return Response(result_serializer.data)
                
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Employee not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except PayrollPeriod.DoesNotExist:
                return Response(
                    {'error': 'Payroll period not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': f'Calculation failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payroll statistics"""
        # Get query parameters
        period_id = request.query_params.get('period_id')
        
        # Build queryset
        queryset = self.get_queryset()
        if period_id:
            queryset = queryset.filter(payroll_period_id=period_id)
        
        # Calculate statistics
        total_payrolls = queryset.count()
        total_amount = queryset.aggregate(total=Sum('net_salary'))['total'] or Decimal('0.00')
        average_salary = queryset.aggregate(avg=Avg('net_salary'))['avg'] or Decimal('0.00')
        
        # Status breakdown
        status_counts = queryset.values('status').annotate(count=Count('id'))
        draft_count = next((item['count'] for item in status_counts if item['status'] == 'DRAFT'), 0)
        calculated_count = next((item['count'] for item in status_counts if item['status'] == 'CALCULATED'), 0)
        approved_count = next((item['count'] for item in status_counts if item['status'] == 'APPROVED'), 0)
        paid_count = next((item['count'] for item in status_counts if item['status'] == 'PAID'), 0)
        
        # Department breakdown
        department_breakdown = list(
            queryset.values('employee__department__name')
            .annotate(
                count=Count('id'),
                total_amount=Sum('net_salary'),
                avg_salary=Avg('net_salary')
            )
            .order_by('-total_amount')
        )
        
        # Monthly trends (last 12 months)
        monthly_trends = list(
            queryset.extra(
                select={'month': "strftime('%%Y-%%m', created_at)"}
            ).values('month').annotate(
                count=Count('id'),
                total_amount=Sum('net_salary'),
                avg_salary=Avg('net_salary')
            ).order_by('month')
        )
        
        # Top earners
        top_earners = list(
            queryset.values(
                'employee__employee_id',
                'employee__first_name',
                'employee__last_name'
            ).annotate(
                total_salary=Sum('net_salary')
            ).order_by('-total_salary')[:10]
        )
        
        stats_data = {
            'total_payrolls': total_payrolls,
            'total_amount': total_amount,
            'average_salary': average_salary,
            'draft_count': draft_count,
            'calculated_count': calculated_count,
            'approved_count': approved_count,
            'paid_count': paid_count,
            'department_breakdown': department_breakdown,
            'monthly_trends': monthly_trends,
            'top_earners': top_earners,
        }
        
        serializer = PayrollStatsSerializer(stats_data)
        return Response(serializer.data)


class PaySlipViewSet(viewsets.ModelViewSet):
    """ViewSet for PaySlip CRUD operations"""
    
    queryset = PaySlip.objects.select_related(
        'payroll__employee', 'payroll__payroll_period', 'generated_by'
    ).all()
    serializer_class = PaySlipSerializer
    permission_classes = [CanManagePayroll]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'slip_number', 'payroll__employee__first_name',
        'payroll__employee__last_name', 'payroll__employee__employee_id'
    ]
    ordering_fields = ['generated_at', 'slip_number']
    ordering = ['-generated_at']
    filterset_fields = ['payroll__payroll_period', 'payroll__employee']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own pay slips
        if not self.request.user.is_staff and not self.request.user.groups.filter(
            name__in=['HR', 'Finance']
        ).exists():
            queryset = queryset.filter(payroll__employee=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set generated_by to current user"""
        serializer.save(generated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_payslips(self, request):
        """Get current user's pay slips"""
        payslips = self.get_queryset().filter(payroll__employee=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(payslips)
        if page is not None:
            serializer = PaySlipSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaySlipSerializer(payslips, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def email(self, request, pk=None):
        """Email pay slip to employee"""
        payslip = self.get_object()
        email = request.data.get('email') or payslip.payroll.employee.email
        
        if not email:
            return Response(
                {'error': 'No email address provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Here you would implement email sending logic
            # For now, just update the email tracking fields
            payslip.emailed_to = email
            payslip.emailed_at = timezone.now()
            payslip.save()
            
            return Response({
                'message': f'Pay slip emailed to {email} successfully.'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to email pay slip: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

