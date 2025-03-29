from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

from customers.models import Customer
from users.models import User


class Loan(models.Model):
    """Loan model representing a customer's loan"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACTIVE = 'ACTIVE', _('Active')
        PAID = 'PAID', _('Paid')
        DEFAULTED = 'DEFAULTED', _('Defaulted')
        RESTRUCTURED = 'RESTRUCTURED', _('Restructured')
        WRITTEN_OFF = 'WRITTEN_OFF', _('Written Off')
    
    # Basic Loan Details
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loans',
        verbose_name=_('customer')
    )
    loan_reference = models.CharField(_('loan reference'), max_length=20, unique=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Loan Amounts
    principal_amount = models.DecimalField(
        _('principal amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    interest_rate = models.DecimalField(
        _('interest rate (%)'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Loan Dates
    application_date = models.DateField(_('application date'), auto_now_add=True)
    approval_date = models.DateField(_('approval date'), null=True, blank=True)
    disbursement_date = models.DateField(_('disbursement date'), null=True, blank=True)
    first_payment_date = models.DateField(_('first payment date'), null=True, blank=True)
    maturity_date = models.DateField(_('maturity date'), null=True, blank=True)
    
    # Loan Terms
    term_months = models.PositiveIntegerField(_('term (months)'))
    payment_frequency = models.CharField(
        _('payment frequency'),
        max_length=20,
        choices=[
            ('DAILY', _('Daily')),
            ('WEEKLY', _('Weekly')),
            ('BIWEEKLY', _('Bi-weekly')),
            ('MONTHLY', _('Monthly')),
            ('QUARTERLY', _('Quarterly')),
        ],
        default='MONTHLY'
    )
    
    # Loan Performance
    amount_paid = models.DecimalField(
        _('amount paid'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    last_payment_date = models.DateField(_('last payment date'), null=True, blank=True)
    days_past_due = models.PositiveIntegerField(_('days past due'), default=0)
    
    # Assigned Officer and Notes
    assigned_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_loans',
        null=True,
        blank=True,
        limit_choices_to={'role__in': [User.Role.COLLECTION_OFFICER, User.Role.MANAGER]}
    )
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps and Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_loans',
        null=True
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='updated_loans',
        null=True
    )
    
    class Meta:
        verbose_name = _('loan')
        verbose_name_plural = _('loans')
        ordering = ['-application_date']
        permissions = [
            ("approve_loan", "Can approve loans"),
            ("disburse_loan", "Can disburse loans"),
            ("restructure_loan", "Can restructure loans"),
            ("write_off_loan", "Can write off loans"),
        ]
        indexes = [
            models.Index(fields=['loan_reference']),
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['assigned_officer']),
        ]
    
    def __str__(self):
        return f"{self.loan_reference} - {self.customer}"
    
    @property
    def total_amount_due(self):
        """Calculate the total amount due (principal + interest)"""
        interest_amount = (self.principal_amount * self.interest_rate / Decimal('100')) * (Decimal(self.term_months) / Decimal('12'))
        return self.principal_amount + interest_amount
    
    @property
    def remaining_balance(self):
        """Calculate the remaining balance"""
        return self.total_amount_due - self.amount_paid
    
    @property
    def payment_status(self):
        """Return a descriptive payment status"""
        if self.status == self.Status.PAID:
            return "Fully Paid"
        elif self.days_past_due == 0:
            return "Current"
        elif self.days_past_due <= 30:
            return "1-30 Days Late"
        elif self.days_past_due <= 60:
            return "31-60 Days Late"
        elif self.days_past_due <= 90:
            return "61-90 Days Late"
        else:
            return "90+ Days Late"


class Payment(models.Model):
    """Model to track loan payments"""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', _('Cash')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
        CHEQUE = 'CHEQUE', _('Cheque')
        OTHER = 'OTHER', _('Other')
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('loan')
    )
    payment_reference = models.CharField(_('payment reference'), max_length=30, unique=True)
    amount = models.DecimalField(
        _('amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_date = models.DateField(_('payment date'))
    payment_method = models.CharField(
        _('payment method'),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='received_payments',
        null=True,
        verbose_name=_('received by')
    )
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_reference']),
            models.Index(fields=['loan']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"{self.payment_reference} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Override save to update loan amount_paid and last_payment_date"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # Only update loan data for new payments
            # Update loan's amount_paid and last_payment_date
            loan = self.loan
            loan.amount_paid += self.amount
            
            # Check if this payment date is more recent than the last recorded payment
            if not loan.last_payment_date or self.payment_date > loan.last_payment_date:
                loan.last_payment_date = self.payment_date
            
            # Check if loan is fully paid
            if loan.amount_paid >= loan.total_amount_due:
                loan.status = Loan.Status.PAID
            
            loan.save(update_fields=['amount_paid', 'last_payment_date', 'status']) 