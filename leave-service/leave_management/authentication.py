import requests
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
import json
from .exceptions import AuthServiceError, InvalidTokenError, TokenValidationError
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
import jwt

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception as e:
            return None

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Get the token
            token = auth_header.split(' ')[1]
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # Ensure roles is a list
            roles = payload.get('roles', [])
            if isinstance(roles, str):
                roles = [roles]
            
            # Create a custom user object from payload
            user = type('User', (), {
                'is_authenticated': True,
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'name': payload.get('name'),
                'roles': roles,
                'department': payload.get('department'),
                'get': lambda x, default=None: payload.get(x, default)
            })
            
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return 'Bearer'
