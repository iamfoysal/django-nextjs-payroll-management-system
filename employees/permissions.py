from rest_framework import permissions
from django.contrib.auth.models import Group


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsHROrManager(permissions.BasePermission):
    """
    Custom permission for HR and Manager roles.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user is in HR or Manager groups
        return (
            request.user.groups.filter(name__in=['HR', 'Manager']).exists() or
            request.user.is_staff
        )


class IsHROnly(permissions.BasePermission):
    """
    Custom permission for HR role only.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user is in HR group
        return (
            request.user.groups.filter(name='HR').exists() or
            request.user.is_staff
        )


class IsManagerOrAbove(permissions.BasePermission):
    """
    Custom permission for Manager and above roles.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user is in Manager, HR, or Admin groups
        return (
            request.user.groups.filter(name__in=['Manager', 'HR', 'Admin']).exists() or
            request.user.is_staff
        )


class CanViewEmployeeData(permissions.BasePermission):
    """
    Permission to view employee data based on role hierarchy.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR can view all employee data
        if request.user.groups.filter(name='HR').exists():
            return True
        
        # Managers can view their subordinates' data
        if request.user.groups.filter(name='Manager').exists():
            return True
        
        # Regular employees can only view their own data
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR can view all employee data
        if request.user.groups.filter(name='HR').exists():
            return True
        
        # Managers can view their subordinates' data
        if request.user.groups.filter(name='Manager').exists():
            # Check if the employee is a subordinate
            if hasattr(obj, 'manager') and obj.manager == request.user:
                return True
            # Check if the employee is in the same department and user is department head
            if (hasattr(obj, 'department') and obj.department and 
                obj.department.head_of_department == request.user):
                return True
        
        # Employees can only view their own data
        return obj == request.user


class CanManageAttendance(permissions.BasePermission):
    """
    Permission to manage attendance records.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR and Managers can manage attendance
        if request.user.groups.filter(name__in=['HR', 'Manager']).exists():
            return True
        
        # Regular employees can manage their own attendance
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR can manage all attendance records
        if request.user.groups.filter(name='HR').exists():
            return True
        
        # Managers can manage their subordinates' attendance
        if request.user.groups.filter(name='Manager').exists():
            if hasattr(obj, 'employee'):
                employee = obj.employee
                # Check if the employee is a subordinate
                if employee.manager == request.user:
                    return True
                # Check if the employee is in the same department and user is department head
                if (employee.department and 
                    employee.department.head_of_department == request.user):
                    return True
        
        # Employees can only manage their own attendance
        return hasattr(obj, 'employee') and obj.employee == request.user


class CanApproveLeave(permissions.BasePermission):
    """
    Permission to approve leave applications.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only HR and Managers can approve leave
        return (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'Manager']).exists()
        )

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR can approve all leave applications
        if request.user.groups.filter(name='HR').exists():
            return True
        
        # Managers can approve their subordinates' leave
        if request.user.groups.filter(name='Manager').exists():
            if hasattr(obj, 'employee'):
                employee = obj.employee
                # Check if the employee is a subordinate
                if employee.manager == request.user:
                    return True
                # Check if the employee is in the same department and user is department head
                if (employee.department and 
                    employee.department.head_of_department == request.user):
                    return True
        
        return False


class CanManagePayroll(permissions.BasePermission):
    """
    Permission to manage payroll data.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only HR and Finance roles can manage payroll
        return (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'Finance', 'Admin']).exists()
        )

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have all permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # HR and Finance can manage all payroll data
        if request.user.groups.filter(name__in=['HR', 'Finance', 'Admin']).exists():
            return True
        
        # Employees can only view their own payroll data (read-only)
        if request.method in permissions.SAFE_METHODS:
            return hasattr(obj, 'employee') and obj.employee == request.user
        
        return False


class CanViewReports(permissions.BasePermission):
    """
    Permission to view reports.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # HR, Managers, and Finance can view reports
        return (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'Manager', 'Finance', 'Admin']).exists()
        )


class CanGenerateReports(permissions.BasePermission):
    """
    Permission to generate reports.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only HR and Finance can generate reports
        return (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'Finance', 'Admin']).exists()
        )

