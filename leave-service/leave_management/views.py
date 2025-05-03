from django.shortcuts import render

# Create your views here.

# leave_management/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from .models import Employee, LeaveType, LeaveBalance, LeaveRequest, LeaveDocument
from .serializers import (EmployeeSerializer, LeaveTypeSerializer, LeaveBalanceSerializer,
                         LeaveRequestSerializer, LeaveDocumentSerializer)
import datetime
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404
from uuid import UUID
from .permissions import IsManagerOrAdmin, IsOwnerOrManagerOrAdmin

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        # Get current employee from auth token
        user_id = request.user.get('id')
        try:
            employee = Employee.objects.get(user_id=user_id)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            # Create new employee
            data = {
                'user_id': user_id,
                'email': request.user.get('email'),
                'name': request.user.get('name'),
                'department': request.user.get('department'),
                'profile_picture': request.user.get('profilePicture')
            }
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    
    @action(detail=False, methods=['get'])
    def my_balances(self, request):
        user_id = request.user.get('id')
        try:
            employee = Employee.objects.get(user_id=user_id)
            current_year = datetime.datetime.now().year
            balances = LeaveBalance.objects.filter(employee=employee, year=current_year)
            serializer = self.get_serializer(balances, many=True)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManagerOrAdmin]
    
    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return super().get_permissions()
    
    def get_object(self):
        """
        Retrieve leave request and check permissions
        """
        # Check if UUID is valid
        try:
            UUID(self.kwargs['pk'])
        except ValueError:
            raise NotFound('Invalid leave request ID format')
            
        # Get leave request or return 404
        obj = get_object_or_404(LeaveRequest, pk=self.kwargs['pk'])
        
        # Check if user has permission
        user = self.request.user
        roles = getattr(user, 'roles', [])
        
        if not ('ROLE_ADMIN' in roles or 'ROLE_MANAGER' in roles):
            try:
                employee = Employee.objects.get(user_id=user.id)
                if obj.employee.id != employee.id:
                    raise PermissionDenied('You do not have permission to access this leave request')
            except Employee.DoesNotExist:
                raise PermissionDenied('Employee not found')
                
        return obj

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'roles'):
            return LeaveRequest.objects.none()
            
        roles = getattr(user, 'roles', [])
        
        if 'ROLE_ADMIN' in roles or 'ROLE_MANAGER' in roles:
            return LeaveRequest.objects.all().order_by('-created_at')
        else:
            try:
                employee = Employee.objects.get(user_id=user.id)
                return LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
            except Employee.DoesNotExist:
                return LeaveRequest.objects.none()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        
        # Check if request can be approved
        if leave_request.status != 'pending':
            return Response(
                {'error': f'Cannot approve leave request with status: {leave_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process approval
        try:
            leave_request.status = 'approved'
            leave_request.comments = request.data.get('comments', '')
            leave_request.save()
            
            # Update leave balance
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            )
            
            duration = (leave_request.end_date - leave_request.start_date).days + 1
            balance.used += duration
            balance.save()
            
            serializer = self.get_serializer(leave_request)
            return Response(serializer.data)
            
        except LeaveBalance.DoesNotExist:
            return Response(
                {'error': 'Leave balance not found for this request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = 'rejected'
        leave_request.comments = request.data.get('comments', '')
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)