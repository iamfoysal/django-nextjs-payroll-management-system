from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import Employee
from .serializers import (
    EmployeeDetailSerializer, EmployeeCreateSerializer, 
    EmployeePasswordChangeSerializer
)
from .permissions import IsHROrManager


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['employee_id'] = user.employee_id
        token['full_name'] = user.get_full_name()
        token['department'] = user.department.name if user.department else None
        token['role'] = user.role.title if user.role else None
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        
        # Add user groups/roles
        token['groups'] = list(user.groups.values_list('name', flat=True))
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to response
        user = self.user
        data['user'] = {
            'id': user.id,
            'employee_id': user.employee_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'department': user.department.name if user.department else None,
            'role': user.role.title if user.role else None,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'groups': list(user.groups.values_list('name', flat=True)),
            'last_login': user.last_login,
        }
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with additional user data"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    """View for employee registration (HR only)"""
    
    permission_classes = [IsHROrManager]
    
    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            employee = serializer.save()
            
            # Assign default role/group if specified
            default_group = request.data.get('default_group', 'Employee')
            try:
                group = Group.objects.get(name=default_group)
                employee.groups.add(group)
            except Group.DoesNotExist:
                pass
            
            # Return employee data
            response_serializer = EmployeeDetailSerializer(employee)
            return Response({
                'message': 'Employee registered successfully.',
                'employee': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """View for user logout (blacklist refresh token)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Successfully logged out.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Invalid token or logout failed.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """View for user profile management"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        serializer = EmployeeDetailSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user profile"""
        serializer = EmployeeDetailSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """View for changing user password"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = EmployeePasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """Get current user's permissions and roles"""
    user = request.user
    
    permissions_data = {
        'user_id': user.id,
        'employee_id': user.employee_id,
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'groups': list(user.groups.values_list('name', flat=True)),
        'permissions': {
            'can_view_all_employees': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Manager']).exists()
            ),
            'can_manage_employees': (
                user.is_staff or 
                user.groups.filter(name='HR').exists()
            ),
            'can_view_attendance': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Manager']).exists()
            ),
            'can_manage_attendance': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Manager']).exists()
            ),
            'can_approve_leave': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Manager']).exists()
            ),
            'can_view_payroll': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Finance']).exists()
            ),
            'can_manage_payroll': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Finance']).exists()
            ),
            'can_view_reports': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Manager', 'Finance']).exists()
            ),
            'can_generate_reports': (
                user.is_staff or 
                user.groups.filter(name__in=['HR', 'Finance']).exists()
            ),
        }
    }
    
    return Response(permissions_data)


@api_view(['POST'])
@permission_classes([IsHROrManager])
def assign_role(request):
    """Assign role/group to an employee"""
    employee_id = request.data.get('employee_id')
    group_name = request.data.get('group_name')
    
    if not employee_id or not group_name:
        return Response({
            'error': 'employee_id and group_name are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        employee = Employee.objects.get(id=employee_id)
        group = Group.objects.get(name=group_name)
        
        # Remove from all groups first (optional)
        if request.data.get('replace_existing', False):
            employee.groups.clear()
        
        # Add to new group
        employee.groups.add(group)
        
        return Response({
            'message': f'Role {group_name} assigned to {employee.get_full_name()} successfully.'
        })
    
    except Employee.DoesNotExist:
        return Response({
            'error': 'Employee not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Group.DoesNotExist:
        return Response({
            'error': 'Role/Group not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsHROrManager])
def remove_role(request):
    """Remove role/group from an employee"""
    employee_id = request.data.get('employee_id')
    group_name = request.data.get('group_name')
    
    if not employee_id or not group_name:
        return Response({
            'error': 'employee_id and group_name are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        employee = Employee.objects.get(id=employee_id)
        group = Group.objects.get(name=group_name)
        
        # Remove from group
        employee.groups.remove(group)
        
        return Response({
            'message': f'Role {group_name} removed from {employee.get_full_name()} successfully.'
        })
    
    except Employee.DoesNotExist:
        return Response({
            'error': 'Employee not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Group.DoesNotExist:
        return Response({
            'error': 'Role/Group not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_roles(request):
    """Get list of available roles/groups"""
    groups = Group.objects.all().values('id', 'name')
    return Response(list(groups))


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_role(request):
    """Create a new role/group (Admin only)"""
    name = request.data.get('name')
    
    if not name:
        return Response({
            'error': 'Role name is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        group, created = Group.objects.get_or_create(name=name)
        
        if created:
            return Response({
                'message': f'Role {name} created successfully.',
                'role': {'id': group.id, 'name': group.name}
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': f'Role {name} already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': f'Failed to create role: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

