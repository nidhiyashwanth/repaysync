from django.contrib import admin
from .models import Loan, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_reference', 'created_at', 'updated_at')
    fields = ('payment_reference', 'amount', 'payment_date', 'payment_method', 
              'received_by', 'notes', 'created_at')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_reference', 'customer', 'status', 'principal_amount', 
                    'interest_rate', 'application_date', 'maturity_date', 
                    'days_past_due', 'assigned_officer')
    list_filter = ('status', 'application_date', 'assigned_officer', 'payment_frequency')
    search_fields = ('loan_reference', 'customer__first_name', 'customer__last_name', 
                    'customer__primary_phone', 'notes')
    readonly_fields = ('loan_reference', 'amount_paid', 'last_payment_date', 
                       'created_at', 'updated_at', 'created_by', 'updated_by')
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'loan_reference', 'status', 'assigned_officer')
        }),
        ('Loan Details', {
            'fields': (('principal_amount', 'interest_rate'), ('term_months', 'payment_frequency'))
        }),
        ('Dates', {
            'fields': (('application_date', 'approval_date'), 
                      ('disbursement_date', 'first_payment_date', 'maturity_date'))
        }),
        ('Payment Status', {
            'fields': (('amount_paid', 'last_payment_date'), 'days_past_due', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    inlines = [PaymentInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
            
            # Generate a loan reference if not provided
            if not obj.loan_reference:
                import uuid
                obj.loan_reference = f"LN-{str(uuid.uuid4())[:8].upper()}"
                
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'loan', 'amount', 'payment_date', 
                   'payment_method', 'received_by')
    list_filter = ('payment_method', 'payment_date', 'received_by')
    search_fields = ('payment_reference', 'loan__loan_reference', 
                    'loan__customer__first_name', 'loan__customer__last_name', 'notes')
    readonly_fields = ('payment_reference', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            # Generate a payment reference if not provided
            if not obj.payment_reference:
                import uuid
                obj.payment_reference = f"PMT-{str(uuid.uuid4())[:8].upper()}"
                
            # Set the receiver to the current user if not specified
            if not obj.received_by:
                obj.received_by = request.user
                
        super().save_model(request, obj, form, change) 