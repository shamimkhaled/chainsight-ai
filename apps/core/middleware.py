import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log request details for monitoring and debugging
    """

    def process_request(self, request):
        # Store request start time
        request.start_time = time.time()

        # Log request details
        logger.info(f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")

    def process_response(self, request, response):
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())

        # Log response details
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.path} "
            f"in {duration:.2f}s"
        )

        return response


class ExceptionLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log exceptions
    """

    def process_exception(self, request, exception):
        logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True
        )


class TenantContextMiddleware(MiddlewareMixin):
    """
    Middleware to ensure tenant context is properly set
    """

    def process_request(self, request):
        # This is handled by TenantMiddleware, but we can add additional context here
        if hasattr(request, 'tenant') and request.tenant:
            # Set tenant in logging context
            logger.info(f"Tenant context: {request.tenant.name} ({request.tenant.subdomain})")


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware for rate limiting (placeholder for future implementation)
    """

    def process_request(self, request):
        # Placeholder for rate limiting logic
        # In production, this would check request rates against tenant limits
        pass