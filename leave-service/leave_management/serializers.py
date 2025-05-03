# leave_management/serializers.py
from rest_framework import serializers
from .models import Employee, LeaveType, LeaveBalance, LeaveRequest, LeaveDocument

class EmployeeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user_id', 'email', 'name', 'department', 'profile_picture', 'created_at', 'updated_at']

class LeaveTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'description', 'default_days', 'requires_approval', 'requires_document', 'created_at', 'updated_at']

class LeaveBalanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = ['id', 'employee', 'leave_type', 'leave_type_name', 'year', 'balance', 'used', 'created_at', 'updated_at']

class LeaveDocumentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = LeaveDocument
        fields = ['id', 'document', 'created_at']

class LeaveRequestSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    documents = LeaveDocumentSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    
    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'duration', 'reason', 'status', 'comments',
            'created_at', 'updated_at', 'documents'
        ]