from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator

from users.models import User


class Customer(models.Model):
    """Customer model representing loan borrowers"""
    
    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')
    
    # Personal Information
    first_name = models.CharField(_('first name'), max_length=50, default="")
    last_name = models.CharField(_('last name'), max_length=50, default="")
    gender = models.CharField(_('gender'), max_length=10, choices=Gender.choices, default=Gender.MALE)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    national_id = models.CharField(_('national ID'), max_length=20, unique=True, blank=True, null=True)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    primary_phone = models.CharField(
        _('primary phone'), 
        validators=[phone_regex], 
        max_length=15,
        default=""
    )
    secondary_phone = models.CharField(
        _('secondary phone'), 
        validators=[phone_regex], 
        max_length=15, 
        blank=True
    )
    email = models.EmailField(
        _('email address'), 
        validators=[EmailValidator()], 
        blank=True
    )
    
    # Address Information
    address = models.CharField(_('address'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state/province'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    # Employment Information
    employer = models.CharField(_('employer'), max_length=255, blank=True)
    job_title = models.CharField(_('job title'), max_length=100, blank=True)
    monthly_income = models.DecimalField(
        _('monthly income'), 
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Loan Officer Assignment
    assigned_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_customers',
        null=True,
        blank=True,
        limit_choices_to={'role': User.Role.COLLECTION_OFFICER}
    )
    
    # Metadata
    is_active = models.BooleanField(_('active'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    risk_score = models.IntegerField(_('risk score'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='created_customers', 
        null=True, 
        blank=True
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='updated_customers', 
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['primary_phone']),
            models.Index(fields=['national_id']),
            models.Index(fields=['last_name', 'first_name']),
        ]
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return the customer's full name."""
        return f"{self.first_name} {self.last_name}"
