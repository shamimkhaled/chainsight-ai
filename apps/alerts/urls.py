from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.alerts.views import AlertRuleViewSet, AlertViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register(r'alerts/rules', AlertRuleViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'alerts/notifications', NotificationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

