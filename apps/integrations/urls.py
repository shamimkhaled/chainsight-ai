from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.integrations.views import (
    IntegrationViewSet,
    WordIntegrationView,
    ERPEntityViewSet
)

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet)
router.register(r'integrations/word', WordIntegrationView, basename='word-integration')
router.register(r'integrations/erp-entities', ERPEntityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

