from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, DepartmentViewSet, RoleViewSet, EmployeeDocumentViewSet
)
from .auth_views import (
    CustomTokenObtainPairView, RegisterView, LogoutView, ProfileView,
    ChangePasswordView, user_permissions, assign_role, remove_role,
    available_roles, create_role
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'documents', EmployeeDocumentViewSet, basename='employee-document')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/permissions/', user_permissions, name='user_permissions'),
    
    # Role management endpoints
    path('roles/assign/', assign_role, name='assign_role'),
    path('roles/remove/', remove_role, name='remove_role'),
    path('roles/available/', available_roles, name='available_roles'),
    path('roles/create/', create_role, name='create_role'),
    
    # API endpoints
    path('api/', include(router.urls)),
]

# Add router URLs
urlpatterns += router.urls

