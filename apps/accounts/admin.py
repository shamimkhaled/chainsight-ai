from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from apps.accounts.models import User, WaitlistEntry, DemoRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for User model"""
    
    list_display = [
        'email', 'full_name', 'tenant_link', 'role',
        'is_active', 'is_verified', 'last_login'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_verified', 'is_staff',
        'is_superuser', 'last_login'
    ]
    
    search_fields = [
        'email', 'first_name', 'last_name',
        'phone', 'tenant__name'
    ]
    
    readonly_fields = [
        'id', 'last_login'
    ]
    
    fieldsets = (
        ('Authentication', {
            'fields': (
                'id', 'email', 'password', 'is_verified'
            )
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 'last_name', 'phone'
            )
        }),
        ('Tenant & Role', {
            'fields': ('tenant', 'role')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_login',),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'tenant',
                'role', 'first_name', 'last_name'
            )
        }),
    )
    
    ordering = ['-created_at']
    filter_horizontal = ['groups', 'user_permissions']
    
    actions = ['verify_users', 'activate_users', 'deactivate_users']
    
    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name() or '-'
    full_name.short_description = 'Full Name'
    
    def tenant_link(self, obj):
        """Display tenant as link"""
        if obj.tenant:
            return format_html(
                '<a href="/admin/tenants/tenant/{}/change/">{}</a>',
                obj.tenant.id, obj.tenant.name
            )
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        from django.utils import timezone
        updated = queryset.update(
            is_verified=True,
            email_verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} user(s) verified.')
    verify_users.short_description = 'Verify selected users'
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    """Admin interface for Waitlist entries"""
    
    list_display = [
        'email', 'company_name', 'status',
        'interest_level', 'created_at'
    ]
    
    list_filter = [
        'status', 'interest_level', 'created_at'
    ]
    
    search_fields = [
        'email', 'company_name', 'first_name',
        'last_name', 'phone'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'id', 'email', 'first_name', 'last_name', 'phone',
                'company_name', 'job_title'
            )
        }),
        ('Status & Interest', {
            'fields': (
                'status', 'interest_level', 'referral_source'
            )
        }),
        ('Communication', {
            'fields': (
                'email_opt_in', 'sms_opt_in'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_contacted', 'mark_as_qualified', 'mark_as_converted']
    
    def mark_as_contacted(self, request, queryset):
        """Mark as contacted"""
        updated = queryset.update(status='contacted')
        self.message_user(request, f'{updated} entry(s) marked as contacted.')
    mark_as_contacted.short_description = 'Mark as contacted'
    
    def mark_as_qualified(self, request, queryset):
        """Mark as qualified"""
        updated = queryset.update(status='qualified')
        self.message_user(request, f'{updated} entry(s) qualified.')
    mark_as_qualified.short_description = 'Mark as qualified'
    
    def mark_as_converted(self, request, queryset):
        """Mark as converted"""
        updated = queryset.update(status='converted')
        self.message_user(request, f'{updated} entry(s) converted.')
    mark_as_converted.short_description = 'Mark as converted'


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    """Admin interface for Demo requests"""
    
    list_display = [
        'email', 'company_name', 'status',
        'preferred_date', 'created_at'
    ]
    
    list_filter = [
        'status', 'created_at', 'preferred_date'
    ]
    
    search_fields = [
        'email', 'company_name', 'first_name',
        'last_name', 'phone'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': (
                'id', 'email', 'first_name', 'last_name', 'phone',
                'company_name', 'job_title'
            )
        }),
        ('Demo Details', {
            'fields': (
                'preferred_date', 'preferred_time', 'timezone',
                'industry', 'company_size', 'attendees'
            )
        }),
        ('Status & Scheduling', {
            'fields': (
                'status', 'scheduled_date', 'meeting_link'
            )
        }),
        ('Follow-up', {
            'fields': (
                'follow_up_required', 'follow_up_date', 'notes'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_scheduled', 'mark_as_completed', 'mark_as_no_show']
    
    def mark_as_scheduled(self, request, queryset):
        """Mark as scheduled"""
        updated = queryset.update(status='scheduled')
        self.message_user(request, f'{updated} demo(s) scheduled.')
    mark_as_scheduled.short_description = 'Mark as scheduled'
    
    def mark_as_completed(self, request, queryset):
        """Mark as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} demo(s) completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_no_show(self, request, queryset):
        """Mark as no show"""
        updated = queryset.update(status='no_show')
        self.message_user(request, f'{updated} demo(s) marked as no show.')
    mark_as_no_show.short_description = 'Mark as no show'
