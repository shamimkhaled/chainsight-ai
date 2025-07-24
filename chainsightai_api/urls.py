
from django.contrib import admin
from django.urls import path

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView



schema_view = get_schema_view(
    openapi.Info(
        title="ChainSight Contract AI API",
        default_version='v1',
        description="AI-powered contract analysis API with OpenAI and OCR support",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@chainsight.ai"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('contract_app.urls')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Redirect the root URL to the Swagger UI documentation
    path('', RedirectView.as_view(url='api/docs/', permanent=False), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

