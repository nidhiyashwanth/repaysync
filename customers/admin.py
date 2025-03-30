from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'primary_phone', 'email', 'branch', 'paid_status', 'assigned_officer', 'is_active')
    list_filter = ('gender', 'is_active', 'paid_status', 'city', 'state', 'branch', 'country', 'assigned_officer', 'created_at')
    search_fields = ('first_name', 'last_name', 'primary_phone', 'email', 'national_id', 'branch')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Personal Information', {
            'fields': (('first_name', 'last_name'), 'gender', 'date_of_birth', 'national_id')
        }),
        ('Contact Information', {
            'fields': ('primary_phone', 'secondary_phone', 'email')
        }),
        ('Address', {
            'fields': ('address', ('city', 'state'), ('postal_code', 'country'), 'branch')
        }),
        ('Employment', {
            'fields': ('employer', 'job_title', 'monthly_income')
        }),
        ('Management', {
            'fields': ('assigned_officer', 'is_active', 'paid_status', 'risk_score', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
