from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class ReportTemplate(models.Model):
    """Template for generating reports"""
    REPORT_TYPES = [
        ('financial', 'Financial Report'),
        ('inventory', 'Inventory Report'),
        ('sales', 'Sales Report'),
        ('purchase', 'Purchase Report'),
        ('customer', 'Customer Report'),
        ('supplier', 'Supplier Report'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    template_content = models.TextField(help_text="HTML template content")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"


class ReportSchedule(models.Model):
    """Schedule for automatic report generation"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=200)
    report_template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
    
    class Meta:
        verbose_name = "Report Schedule"
        verbose_name_plural = "Report Schedules"


class ReportLog(models.Model):
    """Log of generated reports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.report_name} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Report Log"
        verbose_name_plural = "Report Logs"
        ordering = ['-generated_at']
