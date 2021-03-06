import time
from functools import wraps

from rest_framework.exceptions import PermissionDenied


def has_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()
        """"
        allow user request based roles
        and privileges
        """
        if hasattr(cls,'request') and hasattr(cls.request,'user'):
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap

def has_admin_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()
        """"
        allow user request based roles
        and privileges
        """
        if hasattr(cls,'request') and hasattr(cls.request, 'user'):
            print(cls.request.user)
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            if cls.request.user.is_superuser != True:
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap