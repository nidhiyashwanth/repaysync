from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model with role-based access control"""
    
    class Role(models.TextChoices):
        SUPER_MANAGER = 'SUPER_MANAGER', _('Super Manager')
        MANAGER = 'MANAGER', _('Manager')
        COLLECTION_OFFICER = 'COLLECTION_OFFICER', _('Collection Officer')
        CALLING_AGENT = 'CALLING_AGENT', _('Calling Agent')
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=15, blank=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.COLLECTION_OFFICER
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_super_manager(self):
        return self.role == self.Role.SUPER_MANAGER
    
    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER
    
    @property
    def is_collection_officer(self):
        return self.role == self.Role.COLLECTION_OFFICER
    
    @property
    def is_calling_agent(self):
        return self.role == self.Role.CALLING_AGENT


class Hierarchy(models.Model):
    """Model for representing organizational hierarchy"""
    
    manager = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='managed_officers',
        limit_choices_to={'role__in': [User.Role.MANAGER, User.Role.SUPER_MANAGER]}
    )
    collection_officer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reporting_managers',
        limit_choices_to={'role': User.Role.COLLECTION_OFFICER}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('hierarchy')
        verbose_name_plural = _('hierarchies')
        unique_together = ('manager', 'collection_officer')
        ordering = ['manager__username', 'collection_officer__username']
    
    def __str__(self):
        return f"{self.collection_officer} reports to {self.manager}"
        
    def clean(self):
        """Validate that hierarchy makes sense"""
        from django.core.exceptions import ValidationError
        
        if self.manager == self.collection_officer:
            raise ValidationError(_("A user cannot be their own manager."))
        
        if self.manager.role not in [User.Role.MANAGER, User.Role.SUPER_MANAGER]:
            raise ValidationError(_("Manager must have Manager or Super Manager role."))
            
        if self.collection_officer.role != User.Role.COLLECTION_OFFICER:
            raise ValidationError(_("Collection officer must have Collection Officer role."))
