
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API documentation schema view
schema_view = get_schema_view(
    openapi.Info(
        title="ChainSight AI API",
        default_version='v1',
        description="API documentation for ChainSight AI",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@chainsight.ai"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[],  # Allow public access to API docs
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v2 endpoints
    path('api/v2/', include([
        # Authentication
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # Apps
        path('', include('apps.accounts.urls')),
        path('', include('apps.contracts.urls')),
        path('', include('apps.tenants.urls')),
        path('', include('apps.counterparties.urls')),
        path('', include('apps.dashboard.urls')),
        # path('', include('apps.suppliers.urls')),
        # path('', include('apps.alerts.urls')),
        # path('', include('apps.analysis.urls')),
        # path('', include('apps.chat.urls')),
        # path('', include('apps.integrations.urls')),
        # path('', include('apps.repository.urls')),
        # path('', include('apps.compliance.urls')),
    ])),

    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Health check and monitoring
    path('api/health/', include('apps.core.urls')),
]
