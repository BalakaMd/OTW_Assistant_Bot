from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')
        if api_key == settings.AUTH_API_KEY:
            return None, None
        raise AuthenticationFailed('Unauthorized. Please check and provide a valid API key.')
