from django.urls import path
from apps.core.views import HealthCheckView, ReadinessCheckView, APIInfoView

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health'),
    path('ready/', ReadinessCheckView.as_view(), name='ready'),
    path('info/', APIInfoView.as_view(), name='info'),
]

