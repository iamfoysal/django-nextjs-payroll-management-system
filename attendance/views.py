from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Shift, AttendanceRecord, LeaveType, LeaveApplication, OvertimeRequest
)
from .serializers import (
    ShiftSerializer, AttendanceRecordListSerializer, AttendanceRecordDetailSerializer,
    AttendanceRecordCreateSerializer, CheckInSerializer, CheckOutSerializer,
    LeaveTypeSerializer, LeaveApplicationListSerializer, LeaveApplicationDetailSerializer,
    LeaveApplicationCreateSerializer, LeaveApprovalSerializer,
    OvertimeRequestListSerializer, OvertimeRequestDetailSerializer,
    OvertimeRequestCreateSerializer, AttendanceStatsSerializer
)


class ShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for Shift CRUD operations"""
    
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['name', 'start_time', 'created_at']
    ordering = ['start_time']
    filterset_fields = ['shift_type', 'is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active shifts"""
        shifts = Shift.objects.filter(is_active=True)
        serializer = ShiftSerializer(shifts, many=True)
        return Response(serializer.data)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for AttendanceRecord CRUD operations"""
    
    queryset = AttendanceRecord.objects.select_related('employee', 'shift', 'approved_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['date', 'time_in', 'total_hours']
    ordering = ['-date']
    filterset_fields = ['employee', 'date', 'status', 'shift']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AttendanceRecordListSerializer
        elif self.action == 'create':
            return AttendanceRecordCreateSerializer
        else:
            return AttendanceRecordDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions and query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Non-admin users can only see their own records
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Employee check-in"""
        serializer = CheckInSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            today = timezone.now().date()
            now = timezone.now()
            
            # Get or create attendance record
            attendance, created = AttendanceRecord.objects.get_or_create(
                employee=request.user,
                date=today,
                defaults={
                    'time_in': now,
                    'status': 'PRESENT',
                    'check_in_location': serializer.validated_data.get('location', ''),
                    'notes': serializer.validated_data.get('notes', ''),
                    'ip_address': self.get_client_ip(request)
                }
            )
            
            if not created:
                attendance.time_in = now
                attendance.check_in_location = serializer.validated_data.get('location', '')
                attendance.notes = serializer.validated_data.get('notes', '')
                attendance.ip_address = self.get_client_ip(request)
                attendance.save()
            
            return Response({
                'message': 'Checked in successfully.',
                'time_in': attendance.time_in,
                'attendance_id': attendance.id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Employee check-out"""
        serializer = CheckOutSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            today = timezone.now().date()
            now = timezone.now()
            
            try:
                attendance = AttendanceRecord.objects.get(employee=request.user, date=today)
                attendance.time_out = now
                attendance.check_out_location = serializer.validated_data.get('location', '')
                if serializer.validated_data.get('notes'):
                    attendance.notes += f" | Check-out: {serializer.validated_data['notes']}"
                attendance.save()
                
                return Response({
                    'message': 'Checked out successfully.',
                    'time_out': attendance.time_out,
                    'total_hours': attendance.total_hours,
                    'overtime_hours': attendance.overtime_hours
                })
            
            except AttendanceRecord.DoesNotExist:
                return Response(
                    {'error': 'No check-in record found for today.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance record for current user"""
        today = timezone.now().date()
        
        try:
            attendance = AttendanceRecord.objects.get(employee=request.user, date=today)
            serializer = AttendanceRecordDetailSerializer(attendance)
            return Response(serializer.data)
        except AttendanceRecord.DoesNotExist:
            return Response({
                'message': 'No attendance record for today.',
                'date': today,
                'checked_in': False
            })
    
    @action(detail=False, methods=['get'])
    def my_attendance(self, request):
        """Get attendance records for current user"""
        records = self.get_queryset().filter(employee=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = AttendanceRecordListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AttendanceRecordListSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve attendance record"""
        attendance = self.get_object()
        attendance.approved_by = request.user
        attendance.approved_at = timezone.now()
        attendance.save()
        
        return Response({'message': 'Attendance record approved successfully.'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get attendance statistics"""
        # Get query parameters
        employee_id = request.query_params.get('employee_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset
        queryset = self.get_queryset()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        elif not request.user.is_staff:
            queryset = queryset.filter(employee=request.user)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Calculate statistics
        total_records = queryset.count()
        present_days = queryset.filter(status='PRESENT').count()
        absent_days = queryset.filter(status='ABSENT').count()
        late_days = queryset.filter(is_late=True).count()
        leave_days = queryset.filter(status='LEAVE').count()
        
        # Calculate rates
        attendance_rate = (present_days / total_records * 100) if total_records > 0 else 0
        punctuality_rate = ((present_days - late_days) / present_days * 100) if present_days > 0 else 0
        
        # Calculate hours
        hours_data = queryset.aggregate(
            total_hours=Sum('total_hours') or 0,
            regular_hours=Sum('regular_hours') or 0,
            overtime_hours=Sum('overtime_hours') or 0,
            avg_daily_hours=Avg('total_hours') or 0
        )
        
        # Monthly breakdown
        monthly_breakdown = list(
            queryset.extra(
                select={'month': "strftime('%%Y-%%m', date)"}
            ).values('month').annotate(
                total_days=Count('id'),
                present_days=Count('id', filter=Q(status='PRESENT')),
                total_hours=Sum('total_hours'),
                overtime_hours=Sum('overtime_hours')
            ).order_by('month')
        )
        
        # Status breakdown
        status_breakdown = list(
            queryset.values('status').annotate(
                count=Count('id')
            ).order_by('-count')
        )
        
        stats_data = {
            'total_records': total_records,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'leave_days': leave_days,
            'attendance_rate': round(attendance_rate, 2),
            'punctuality_rate': round(punctuality_rate, 2),
            'total_hours': hours_data['total_hours'],
            'regular_hours': hours_data['regular_hours'],
            'overtime_hours': hours_data['overtime_hours'],
            'average_daily_hours': round(hours_data['avg_daily_hours'], 2),
            'monthly_breakdown': monthly_breakdown,
            'status_breakdown': status_breakdown,
        }
        
        serializer = AttendanceStatsSerializer(stats_data)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveType CRUD operations"""
    
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'max_days_per_year', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_paid', 'requires_approval', 'is_active']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active leave types"""
        leave_types = LeaveType.objects.filter(is_active=True)
        serializer = LeaveTypeSerializer(leave_types, many=True)
        return Response(serializer.data)


class LeaveApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for LeaveApplication CRUD operations"""
    
    queryset = LeaveApplication.objects.select_related('employee', 'leave_type', 'approved_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason']
    ordering_fields = ['applied_at', 'start_date', 'end_date']
    ordering = ['-applied_at']
    filterset_fields = ['employee', 'leave_type', 'status', 'start_date', 'end_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return LeaveApplicationListSerializer
        elif self.action == 'create':
            return LeaveApplicationCreateSerializer
        else:
            return LeaveApplicationDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own applications
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get leave applications for current user"""
        applications = self.get_queryset().filter(employee=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = LeaveApplicationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LeaveApplicationListSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get pending leave applications for approval"""
        # Only managers/HR can see pending approvals
        if not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to view pending approvals.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = LeaveApplication.objects.filter(status='PENDING')
        serializer = LeaveApplicationListSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """Approve or reject leave application"""
        application = self.get_object()
        serializer = LeaveApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            if action == 'approve':
                application.approve(request.user)
                message = 'Leave application approved successfully.'
            else:
                application.reject(request.user, reason)
                message = 'Leave application rejected successfully.'
            
            return Response({'message': message})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get leave balance for current user"""
        user = request.user
        
        # Calculate used leave days for current year
        current_year = timezone.now().year
        used_leaves = LeaveApplication.objects.filter(
            employee=user,
            status='APPROVED',
            start_date__year=current_year
        ).aggregate(
            total_days=Sum('total_days')
        )['total_days'] or 0
        
        balance = {
            'annual_leave_balance': user.annual_leave_balance,
            'sick_leave_balance': user.sick_leave_balance,
            'casual_leave_balance': user.casual_leave_balance,
            'used_leaves_this_year': used_leaves,
            'remaining_annual_leave': max(0, user.annual_leave_balance - used_leaves)
        }
        
        return Response(balance)


class OvertimeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for OvertimeRequest CRUD operations"""
    
    queryset = OvertimeRequest.objects.select_related('employee', 'approved_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason']
    ordering_fields = ['requested_at', 'date', 'hours_requested']
    ordering = ['-requested_at']
    filterset_fields = ['employee', 'status', 'date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return OvertimeRequestListSerializer
        elif self.action == 'create':
            return OvertimeRequestCreateSerializer
        else:
            return OvertimeRequestDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own requests
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get overtime requests for current user"""
        requests = self.get_queryset().filter(employee=request.user)
        
        # Apply pagination
        page = self.paginate_queryset(requests)
        if page is not None:
            serializer = OvertimeRequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OvertimeRequestListSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get pending overtime requests for approval"""
        # Only managers/HR can see pending approvals
        if not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to view pending approvals.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = OvertimeRequest.objects.filter(status='PENDING')
        serializer = OvertimeRequestListSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve overtime request"""
        overtime_request = self.get_object()
        overtime_request.status = 'APPROVED'
        overtime_request.approved_by = request.user
        overtime_request.approved_at = timezone.now()
        overtime_request.save()
        
        return Response({'message': 'Overtime request approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject overtime request"""
        overtime_request = self.get_object()
        reason = request.data.get('reason', '')
        
        overtime_request.status = 'REJECTED'
        overtime_request.approved_by = request.user
        overtime_request.approved_at = timezone.now()
        overtime_request.rejection_reason = reason
        overtime_request.save()
        
        return Response({'message': 'Overtime request rejected successfully.'})

