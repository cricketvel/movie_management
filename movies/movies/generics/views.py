import urllib3
from django.conf import settings
from django.utils.decorators import classonlymethod
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.utils.translation import ugettext_lazy as _
from rest_framework.viewsets import ViewSet as RestFrameworkViewSet
from .error_class import ConfigurationError, LogicError, ResponseError, ValidationError
from django.views.decorators.csrf import csrf_exempt
from functools import update_wrapper


class APIView(RestFrameworkViewSet):
    """ Generic api view abstract so it we can reusable methods"""

    DEFAULT_RESPONSE_MESSAGES = {
        status.HTTP_400_BAD_REQUEST: _("Invalid Request"),
        status.HTTP_500_INTERNAL_SERVER_ERROR: _("Server Error."),
        status.HTTP_401_UNAUTHORIZED: _("Unauthorized Request."),
        status.HTTP_200_OK: _("Success"),
        status.HTTP_403_FORBIDDEN: _("Invalid Authentication Credential Provided"),
        status.HTTP_404_NOT_FOUND: _("Invalid API URL Called"),
        status.HTTP_405_METHOD_NOT_ALLOWED: _("Method Not Found"),
    }

    permission_classes = ()

    # permission_classes = (IsAuthenticated,)

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        """
        Because of the way class based views create a closure around the
        instantiated view, we need to totally reimplement `.as_view`,
        and slightly modify the view function that is created and returned.
        """
        # The suffix initkwarg is reserved for displaying the viewset type.
        # eg. 'List' or 'Instance'.
        cls.suffix = None

        # Setting a basename allows a view to reverse its action urls. This
        # value is provided by the router through the initkwargs.
        cls.basename = None

        # actions must not be empty
        if not actions:
            raise TypeError("The `actions` argument must be provided when "
                            "calling `.as_view()` on a ViewSet. For example "
                            "`.as_view({'get': 'list'})`")

        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r" % (
                    cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)

            # We also store the mapping of request methods to actions,
            # so that we can later set the action attribute.
            # eg. `self.action = 'list'` on an incoming GET request.
            self.action_map = actions

            # Bind methods to actions
            # This is the bit that's different to a standard view
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method, handler)
                # UserRequest.set_current_api(action)

            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get


            self.request = request
            self.args = args
            self.kwargs = kwargs

            # And continue as usual
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())

        # We need to set these on the view function, so that breadcrumb
        # generation can pick out these bits of information from a
        # resolved URL.
        view.cls = cls
        view.initkwargs = initkwargs
        view.suffix = initkwargs.get('suffix', None)
        view.actions = actions
        return csrf_exempt(view)

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        set the user instance to the user request class variable
        """
        super(APIView, self).initial(request, *args, **kwargs)

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # UserRequest.set_req_user(request.user)

    @property
    def locale(self):
        """
        By making ugettext_lazy every api viewset have locale
        as instance variable
        """
        return _

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        response = self.get_response_from_exception(exc, self.get_exception_handler_context())


        response.exception = True
        return response

    def exception_handler(self, exc, context):
        """
         Generic error handler for all the exception in application
         it help to maintain response format for all the request when
         debug not enabled
        """
        response = self.get_response_from_exception(exc, context)

        return self.get_response(
            statuscode=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) if settings.DEBUG is False and response is None else response

    def get_response(self, **kwargs):
        """
         Generic method to hold response format of the application
        """
        data = kwargs.get("data", None)
        paginator = kwargs.get("paginator", None)
        statuscode = kwargs.get("statuscode", status.HTTP_200_OK)

        formatted_response = {
            "status": kwargs.get("statuscode", status.HTTP_200_OK),
            "message": kwargs.get("message", self.get_default_response_message(statuscode))
        }

        if paginator:
            formatted_response['total'] = paginator.get('count')
            formatted_response['previous'] = paginator.get('previous')
            formatted_response['next'] = paginator.get('next')
            if paginator.get('total_count_enabled', False):
                formatted_response['total_count'] = paginator.get('total_count')

        if data is not None:
            formatted_response['data'] = data
        else:
            formatted_response['errors'] = kwargs.get("errors", None)

        return Response(data=formatted_response, status=statuscode)

    def get_response_from_exception(self, exc, context):
        """
         Generic method to format the response created by exception like
         rest_framework.exceptions.ValidationError
        """
        if isinstance(exc, ValidationError):
            response = Response(data=str(exc), status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, ConfigurationError):
            response = Response(data=str(exc), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif isinstance(exc, LogicError):
            response = Response(data=str(exc), status=status.HTTP_406_NOT_ACCEPTABLE)
        elif isinstance(exc, ResponseError):
            response = Response(data=exc.get_body(), status=exc.status)
        else:
            response = exception_handler(exc, context)

        if response is None:
            raise Exception(exc)

        return self.get_response(
            errors=response.data,
            statuscode=response.status_code
        ) if response is not None else None

    def get_default_response_message(self, statuscode):
        """
         Get the default message by status code
        """
        return self.DEFAULT_RESPONSE_MESSAGES[statuscode] if statuscode in self.DEFAULT_RESPONSE_MESSAGES else "Success"

    def get_header(self, request=None):
        """
        Get the header value of our requested API
        """
        headers = {'Content-Type': 'application/json'}
        if request is not None:
            headers = {'Content-Type': request.META.get('CONTENT_TYPE'),
                       'Authorization': request.META.get('HTTP_AUTHORIZATION')}
        return headers