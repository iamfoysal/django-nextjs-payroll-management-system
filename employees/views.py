from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Employee, Department, Role, EmployeeDocument
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer,
    EmployeeUpdateSerializer, EmployeePasswordChangeSerializer, DepartmentSerializer,
    RoleSerializer, EmployeeDocumentSerializer, EmployeeStatsSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department CRUD operations"""
    
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active']
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees in this department"""
        department = self.get_object()
        employees = department.employee_set.filter(is_active=True)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get department statistics"""
        departments = Department.objects.annotate(
            employee_count=Count('employee_set', filter=Q(employee_set__is_active=True))
        )
        
        stats = {
            'total_departments': departments.count(),
            'active_departments': departments.filter(is_active=True).count(),
            'departments_with_employees': departments.filter(employee_count__gt=0).count(),
            'largest_department': departments.order_by('-employee_count').first(),
            'department_breakdown': [
                {
                    'name': dept.name,
                    'employee_count': dept.employee_count,
                    'is_active': dept.is_active
                }
                for dept in departments.order_by('-employee_count')[:10]
            ]
        }
        
        return Response(stats)


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role CRUD operations"""
    
    queryset = Role.objects.select_related('department').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'department__name']
    ordering_fields = ['title', 'base_salary', 'hourly_rate', 'created_at']
    ordering = ['title']
    filterset_fields = ['department', 'is_active']
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Get all employees with this role"""
        role = self.get_object()
        employees = role.employee_set.filter(is_active=True)
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get roles grouped by department"""
        department_id = request.query_params.get('department_id')
        if department_id:
            roles = Role.objects.filter(department_id=department_id, is_active=True)
        else:
            roles = Role.objects.filter(is_active=True)
        
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee CRUD operations"""
    
    queryset = Employee.objects.select_related('department', 'role', 'manager').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['employee_id', 'username', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_id', 'first_name', 'last_name', 'hire_date', 'created_at']
    ordering = ['employee_id']
    filterset_fields = ['department', 'role', 'employment_type', 'salary_type', 'is_active']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        elif self.action == 'change_password':
            return EmployeePasswordChangeSerializer
        else:
            return EmployeeDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Add any role-based filtering here
        # For now, return all employees for authenticated users
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change employee password"""
        employee = self.get_object()
        
        # Only allow users to change their own password or admins to change any password
        if request.user != employee and not request.user.is_staff:
            return Response(
                {'error': 'You can only change your own password.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EmployeePasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an employee"""
        employee = self.get_object()
        employee.is_active = False
        employee.termination_date = timezone.now().date()
        employee.save()
        
        return Response({'message': 'Employee deactivated successfully.'})
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate an employee"""
        employee = self.get_object()
        employee.is_active = True
        employee.termination_date = None
        employee.save()
        
        return Response({'message': 'Employee reactivated successfully.'})
    
    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """Get all subordinates of this employee"""
        employee = self.get_object()
        subordinates = employee.subordinates.filter(is_active=True)
        serializer = EmployeeListSerializer(subordinates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for this employee"""
        employee = self.get_object()
        documents = employee.documents.all()
        serializer = EmployeeDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's employee profile"""
        if hasattr(request.user, 'employee_id'):
            serializer = EmployeeDetailSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'User is not an employee.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get employee statistics"""
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Basic counts
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(is_active=True).count()
        inactive_employees = total_employees - active_employees
        
        # Department and role counts
        departments_count = Department.objects.filter(is_active=True).count()
        roles_count = Role.objects.filter(is_active=True).count()
        
        # New hires and terminations this month
        new_hires_this_month = Employee.objects.filter(
            hire_date__gte=current_month_start.date()
        ).count()
        
        terminations_this_month = Employee.objects.filter(
            termination_date__gte=current_month_start.date()
        ).count()
        
        # Department breakdown
        department_breakdown = list(
            Department.objects.annotate(
                employee_count=Count('employee_set', filter=Q(employee_set__is_active=True))
            ).values('name', 'employee_count').order_by('-employee_count')
        )
        
        # Employment type breakdown
        employment_type_breakdown = list(
            Employee.objects.filter(is_active=True)
            .values('employment_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Salary type breakdown
        salary_type_breakdown = list(
            Employee.objects.filter(is_active=True)
            .values('salary_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        stats_data = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'departments_count': departments_count,
            'roles_count': roles_count,
            'new_hires_this_month': new_hires_this_month,
            'terminations_this_month': terminations_this_month,
            'department_breakdown': department_breakdown,
            'employment_type_breakdown': employment_type_breakdown,
            'salary_type_breakdown': salary_type_breakdown,
        }
        
        serializer = EmployeeStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def managers(self, request):
        """Get list of employees who can be managers"""
        managers = Employee.objects.filter(
            is_active=True,
            role__isnull=False
        ).exclude(
            role__title__icontains='intern'
        )
        serializer = EmployeeListSerializer(managers, many=True)
        return Response(serializer.data)


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Employee Document CRUD operations"""
    
    queryset = EmployeeDocument.objects.select_related('employee', 'uploaded_by').all()
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['uploaded_at', 'title']
    ordering = ['-uploaded_at']
    filterset_fields = ['employee', 'document_type']
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user"""
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        """Filter documents based on user permissions"""
        queryset = super().get_queryset()
        
        # Non-admin users can only see their own documents
        if not self.request.user.is_staff:
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get documents for a specific employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        documents = self.get_queryset().filter(employee_id=employee_id)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available document types"""
        types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in EmployeeDocument.DOCUMENT_TYPE_CHOICES
        ]
        return Response(types)

