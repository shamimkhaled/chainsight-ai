from django.contrib import admin
from .models import ContractAnalysis, RateLimitTracker

# Customizing the admin interface for ContractAnalysis
@admin.register(ContractAnalysis)
class ContractAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_ip', 'original_filename', 'industry', 'language', 'status', 'created_at')
    list_filter = ('industry', 'language', 'status')
    search_fields = ('original_filename', 'user_ip')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'processing_started_at', 'processing_completed_at')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(RateLimitTracker)
class RateLimitTrackerAdmin(admin.ModelAdmin):
    list_display = ('user_ip', 'daily_count', 'last_reset_date')
    search_fields = ('user_ip',)
    ordering = ('-last_reset_date',)
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    
    

