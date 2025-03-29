from django.contrib import admin
from .models import Interaction, FollowUp


class FollowUpInline(admin.TabularInline):
    model = FollowUp
    extra = 0
    fields = ('follow_up_type', 'scheduled_date', 'scheduled_time', 'assigned_to', 
              'priority', 'status', 'completed_at', 'completed_by')
    readonly_fields = ('completed_at', 'completed_by')


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'interaction_type', 'initiated_by', 
                    'start_time', 'outcome', 'payment_promise_date')
    list_filter = ('interaction_type', 'outcome', 'initiated_by', 'start_time')
    search_fields = ('customer__first_name', 'customer__last_name', 'notes', 
                     'customer__primary_phone', 'contact_number', 'contact_person')
    readonly_fields = ('duration', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': (('customer', 'loan'), ('interaction_type', 'initiated_by'))
        }),
        ('Contact Details', {
            'fields': (('contact_number', 'contact_person'), ('start_time', 'end_time', 'duration'))
        }),
        ('Outcome', {
            'fields': ('outcome', 'notes', ('payment_promise_amount', 'payment_promise_date'))
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [FollowUpInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.initiated_by:
            obj.initiated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'follow_up_type', 'scheduled_date', 
                    'assigned_to', 'priority', 'status')
    list_filter = ('follow_up_type', 'status', 'priority', 'assigned_to', 'scheduled_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'notes', 
                     'result', 'interaction__notes')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'completed_at', 'completed_by')
    fieldsets = (
        ('Basic Information', {
            'fields': (('interaction', 'customer'), ('follow_up_type', 'priority'))
        }),
        ('Scheduling', {
            'fields': (('scheduled_date', 'scheduled_time'), 'assigned_to')
        }),
        ('Status and Result', {
            'fields': ('status', 'notes', 'result', ('completed_at', 'completed_by'))
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
            
        # If status is being changed to COMPLETED, set completed_at and completed_by
        if 'status' in form.changed_data and obj.status == FollowUp.FollowUpStatus.COMPLETED:
            from django.utils import timezone
            obj.completed_at = timezone.now()
            obj.completed_by = request.user
            
        super().save_model(request, obj, form, change)
