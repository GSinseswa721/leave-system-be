from rest_framework.exceptions import APIException
from rest_framework import status

class AuthServiceError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Authentication service is unavailable.'
    default_code = 'auth_service_error'

class InvalidTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired token.'
    default_code = 'invalid_token'

class TokenValidationError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Token validation failed.'
    default_code = 'token_validation_error'
