# leave_management/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import EmployeeViewSet, LeaveTypeViewSet, LeaveBalanceViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-balances', LeaveBalanceViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]