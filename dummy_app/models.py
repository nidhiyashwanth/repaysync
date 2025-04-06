from django.db import models
from users.models import User


class DummyEntity(models.Model):
    """A dummy entity for testing dynamic permission system"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='owned_dummy_entities'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_dummy_entities',
        null=True,
        blank=True
    )
    is_sensitive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 