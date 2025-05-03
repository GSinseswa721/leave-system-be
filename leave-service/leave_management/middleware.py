from django.http import JsonResponse
from .exceptions import AuthServiceError, InvalidTokenError, TokenValidationError
import logging

logger = logging.getLogger(__name__)

class AuthErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, (AuthServiceError, InvalidTokenError, TokenValidationError)):
            logger.error(f"Auth error: {str(exception)}")
            return JsonResponse({
                'error': str(exception),
                'code': getattr(exception, 'default_code', 'auth_error')
            }, status=exception.status_code)
        return None
