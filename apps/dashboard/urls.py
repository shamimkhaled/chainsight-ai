from django.urls import path
from apps.dashboard.views import (
    DashboardView,
    ContractTrendsView,
    RiskDistributionView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/trends/', ContractTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/risk-distribution/', RiskDistributionView.as_view(), name='dashboard-risk'),
]

