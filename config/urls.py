from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import admin customization
import config.admin  # noqa: F401

# API documentation schema view with Bearer token authentication
schema_view = get_schema_view(
    openapi.Info(
        title="ChainSight AI API",
        default_version='v1',
        description="""
## ChainSight AI - Contract Intelligence Platform

### Authentication
This API uses **JWT Bearer Token** authentication.

**To authenticate:**
1. Get a token from `/api/v1/auth/token/` with your email and password
2. Click the **Authorize** button (🔓) above
3. Enter: `Bearer <your_access_token>`
4. Click **Authorize**

### Token Endpoints
- `POST /api/v1/auth/token/` - Get access and refresh tokens
- `POST /api/v1/auth/token/refresh/` - Refresh access token

### Example Request
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "your_password"}'
```

### Response
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
        """,
        terms_of_service="https://chainsight.ai/terms/",
        contact=openapi.Contact(email="support@chainsight.ai"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1 endpoints
    path('api/v1/', include([
        # Authentication
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

        # Apps
        path('', include('apps.accounts.urls')),
        path('', include('apps.contracts.urls')),
        path('', include('apps.tenants.urls')),
        path('', include('apps.counterparties.urls')),
        path('', include('apps.dashboard.urls')),
        path('', include('apps.chat.urls')),
        path('', include('apps.integrations.urls')),
        path('', include('apps.alerts.urls')),
        # path('', include('apps.suppliers.urls')),
        # path('', include('apps.analysis.urls')),
        # path('', include('apps.repository.urls')),
        # path('', include('apps.compliance.urls')),
    ])),

    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Health check and monitoring
    path('api/health/', include('apps.core.urls')),
]
