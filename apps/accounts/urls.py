from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserViewSet, WaitlistViewSet, DemoViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'waitlist', WaitlistViewSet)
router.register(r'demos', DemoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]