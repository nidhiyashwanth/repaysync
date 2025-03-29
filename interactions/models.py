from django.db import models
from django.utils.translation import gettext_lazy as _

from customers.models import Customer
from users.models import User
from loans.models import Loan


class Interaction(models.Model):
    """Model for tracking interactions with customers"""
    
    class InteractionType(models.TextChoices):
        CALL = 'CALL', _('Phone Call')
        MEETING = 'MEETING', _('In-Person Meeting')
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        VISIT = 'VISIT', _('Field Visit')
        OTHER = 'OTHER', _('Other')
    
    class InteractionOutcome(models.TextChoices):
        PAYMENT_PROMISED = 'PAYMENT_PROMISED', _('Payment Promised')
        PAYMENT_MADE = 'PAYMENT_MADE', _('Payment Made')
        NO_ANSWER = 'NO_ANSWER', _('No Answer')
        WRONG_NUMBER = 'WRONG_NUMBER', _('Wrong Number')
        NUMBER_DISCONNECTED = 'NUMBER_DISCONNECTED', _('Number Disconnected')
        CUSTOMER_UNAVAILABLE = 'CUSTOMER_UNAVAILABLE', _('Customer Unavailable')
        DISPUTED = 'DISPUTED', _('Disputed')
        REFUSED_TO_PAY = 'REFUSED_TO_PAY', _('Refused to Pay')
        OTHER = 'OTHER', _('Other')
    
    # Basic information
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name=_('customer')
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name=_('loan'),
        null=True,
        blank=True
    )
    interaction_type = models.CharField(
        _('interaction type'),
        max_length=20,
        choices=InteractionType.choices
    )
    initiated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='initiated_interactions',
        verbose_name=_('initiated by')
    )
    
    # Interaction details
    contact_number = models.CharField(_('contact number'), max_length=15, blank=True)
    contact_person = models.CharField(_('contact person'), max_length=100, blank=True)
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)
    duration = models.PositiveIntegerField(_('duration (seconds)'), null=True, blank=True)
    
    # Interaction outcome
    outcome = models.CharField(
        _('outcome'),
        max_length=30,
        choices=InteractionOutcome.choices,
        null=True,
        blank=True
    )
    notes = models.TextField(_('notes'))
    payment_promise_amount = models.DecimalField(
        _('payment promise amount'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    payment_promise_date = models.DateField(_('payment promise date'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('interaction')
        verbose_name_plural = _('interactions')
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['loan']),
            models.Index(fields=['initiated_by']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.customer} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if start_time and end_time are present
        if self.start_time and self.end_time and not self.duration:
            time_diff = self.end_time - self.start_time
            self.duration = int(time_diff.total_seconds())
        super().save(*args, **kwargs)


class FollowUp(models.Model):
    """Model for scheduling follow-up actions after interactions"""
    
    class FollowUpType(models.TextChoices):
        CALL = 'CALL', _('Phone Call')
        VISIT = 'VISIT', _('Field Visit')
        SMS = 'SMS', _('SMS Reminder')
        EMAIL = 'EMAIL', _('Email Reminder')
        OTHER = 'OTHER', _('Other')
    
    class FollowUpStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        RESCHEDULED = 'RESCHEDULED', _('Rescheduled')
        CANCELED = 'CANCELED', _('Canceled')
    
    # Basic information
    interaction = models.ForeignKey(
        Interaction,
        on_delete=models.CASCADE,
        related_name='follow_ups',
        verbose_name=_('interaction')
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='follow_ups',
        verbose_name=_('customer')
    )
    follow_up_type = models.CharField(
        _('follow-up type'),
        max_length=20,
        choices=FollowUpType.choices
    )
    
    # Scheduling information
    scheduled_date = models.DateField(_('scheduled date'))
    scheduled_time = models.TimeField(_('scheduled time'), null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_follow_ups',
        verbose_name=_('assigned to')
    )
    
    # Follow-up details
    notes = models.TextField(_('notes'), blank=True)
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=[
            ('LOW', _('Low')),
            ('MEDIUM', _('Medium')),
            ('HIGH', _('High')),
            ('URGENT', _('Urgent')),
        ],
        default='MEDIUM'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=FollowUpStatus.choices,
        default=FollowUpStatus.PENDING
    )
    
    # Follow-up results
    result = models.TextField(_('result'), blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='completed_follow_ups',
        verbose_name=_('completed by'),
        null=True,
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_follow_ups',
        verbose_name=_('created by')
    )
    
    class Meta:
        verbose_name = _('follow-up')
        verbose_name_plural = _('follow-ups')
        ordering = ['status', 'scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.get_follow_up_type_display()} with {self.customer} on {self.scheduled_date}"
