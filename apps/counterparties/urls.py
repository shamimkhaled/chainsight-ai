from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.counterparties.views import CounterpartyViewSet

router = DefaultRouter()
router.register(r'counterparties', CounterpartyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

