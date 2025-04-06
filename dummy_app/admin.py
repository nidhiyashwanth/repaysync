from django.contrib import admin
from .models import DummyEntity


@admin.register(DummyEntity)
class DummyEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'assignee', 'is_sensitive', 'created_at')
    list_filter = ('is_sensitive', 'created_at')
    search_fields = ('name', 'description', 'owner__username', 'assignee__username')
    raw_id_fields = ('owner', 'assignee') 