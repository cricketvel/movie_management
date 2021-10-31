from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions

from users.models import CustomUser as Users



import jwt


class Authentication(JSONWebTokenAuthentication):
    """
    All authentication classes should extend BaseAuthentication.
    """
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        token = self.get_token_value_from_header(request)
        if token is None:
            return None
        try:
            """
            If jwt token available it will decode otherwise it will throw exception.
            """
            value = jwt.decode(token, None, None)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()


        else:
            """
            If access token not available do JWS id token authentication
            """
            from movies.generics.jwt_authentication import JwtAuthentication

            return JwtAuthentication.authenticate(self, request)


    def get_token_value_from_header(self, request):
        """
        Get the token value from header and return token value only
        """
        auth = get_authorization_header(request).split()
        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        if auth:
            return auth[1]
        return None


    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user
        """

        try:
            user = Users.objects.get(id=payload.get('id'), is_active=True)
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid signature.'))

        return user



