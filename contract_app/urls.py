from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contracts', views.ContractAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health-check'),
    path('rate-limit/', views.rate_limit_status, name='rate-limit-status'),
    
    # Create a new waitlist entry
    path('waitlist/join/', views.WaitlistCreateView.as_view(), name='waitlist-join'),

    # Get waitlist statistics
    path('waitlist/stats/', views.waitlist_stats, name='waitlist-stats'),
]