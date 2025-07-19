from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PayrollPeriodViewSet, TaxSlabViewSet, DeductionTypeViewSet,
    BonusTypeViewSet, PayrollViewSet, PaySlipViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'tax-slabs', TaxSlabViewSet, basename='tax-slab')
router.register(r'deduction-types', DeductionTypeViewSet, basename='deduction-type')
router.register(r'bonus-types', BonusTypeViewSet, basename='bonus-type')
router.register(r'payrolls', PayrollViewSet, basename='payroll')
router.register(r'payslips', PaySlipViewSet, basename='payslip')

# URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Add router URLs
urlpatterns += router.urls

