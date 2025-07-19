from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportsViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'reports', ReportsViewSet, basename='reports')

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Add router URLs
urlpatterns += router.urls

