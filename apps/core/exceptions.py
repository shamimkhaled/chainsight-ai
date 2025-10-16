from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST API
    """

    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Add custom error formatting
        custom_response_data = {
            'error': {
                'type': exc.__class__.__name__,
                'message': str(exc),
                'details': response.data if hasattr(response, 'data') else None
            }
        }

        # Add request context if available
        request = context.get('request')
        if request:
            custom_response_data['error']['path'] = request.path
            custom_response_data['error']['method'] = request.method

        response.data = custom_response_data

        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)} "
            f"at {request.path if request else 'unknown path'}"
        )

    return response


class ChainsightException(Exception):
    """
    Base exception for Chainsight application
    """

    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ValidationError(ChainsightException):
    """
    Validation error
    """
    def __init__(self, message, details=None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class AuthenticationError(ChainsightException):
    """
    Authentication error
    """
    def __init__(self, message="Authentication required"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(ChainsightException):
    """
    Authorization error
    """
    def __init__(self, message="Permission denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(ChainsightException):
    """
    Resource not found error
    """
    def __init__(self, message="Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictError(ChainsightException):
    """
    Resource conflict error
    """
    def __init__(self, message="Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class RateLimitError(ChainsightException):
    """
    Rate limit exceeded error
    """
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class ExternalServiceError(ChainsightException):
    """
    External service error
    """
    def __init__(self, message="External service error", details=None):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, details)