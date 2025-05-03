from django.db import models
import uuid
from decimal import Decimal
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']  # Add default ordering

class Employee(BaseModel):
    user_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    profile_picture = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class LeaveType(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    default_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monthly_accrual_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    requires_approval = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    max_carryover_days = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

class LeaveBalance(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    used = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name} ({self.year})"

class LeaveRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

class LeaveDocument(BaseModel):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='leave_documents/')
    
    def __str__(self):
        return f"Document for {self.leave_request}"
