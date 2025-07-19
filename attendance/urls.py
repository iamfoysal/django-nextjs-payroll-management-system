from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShiftViewSet, AttendanceRecordViewSet, LeaveTypeViewSet,
    LeaveApplicationViewSet, OvertimeRequestViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-applications', LeaveApplicationViewSet, basename='leave-application')
router.register(r'overtime-requests', OvertimeRequestViewSet, basename='overtime-request')

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Add custom URL patterns if needed
urlpatterns += router.urls

