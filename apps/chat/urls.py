from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chat.views import ChatSessionViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionViewSet)
router.register(r'chat/messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

