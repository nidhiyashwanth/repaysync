from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Hierarchy


class HierarchyInline(admin.TabularInline):
    model = Hierarchy
    fk_name = 'collection_officer'
    extra = 1
    verbose_name = _("Reporting Manager")
    verbose_name_plural = _("Reporting Managers")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Role information'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    inlines = [HierarchyInline]
    
    def get_inlines(self, request, obj=None):
        """Only show inline if user is a collection officer"""
        if obj and obj.role == User.Role.COLLECTION_OFFICER:
            return [HierarchyInline]
        return []


@admin.register(Hierarchy)
class HierarchyAdmin(admin.ModelAdmin):
    list_display = ('manager', 'collection_officer', 'created_at')
    list_filter = ('manager__role', 'collection_officer__role')
    search_fields = ('manager__username', 'manager__email', 'collection_officer__username', 'collection_officer__email')
    raw_id_fields = ('manager', 'collection_officer')
    date_hierarchy = 'created_at'
