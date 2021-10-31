from rest_framework import status


class ConfigurationError(Exception):
    """
        ConfigurationError is thrown configured value is invalid
    """


class LogicError(Exception):
    """
        LogicError is thrown when logical error occur
    """


class UniqueIdGenerationError(ConfigurationError):
    """
        UniqueIdGenerationError this error commonly
        used when unable to generate unique due to
        various reasons
    """


class ResponseError(Exception):
    """
        Response is a short form to make to response
        by throwing particular response
    """

    def __init__(self, *args, **kwargs):
        """
        class intializer receive error messsage and status code from
        kwargs
        """
        self.status = kwargs.pop('status', status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.message = kwargs.pop('message', None)

        super(ResponseError, self).__init__(*args, **kwargs)


    def get_body(self):
        """
        get the response body
        """
        return self.message


class ValidationError(ResponseError):
    """
        ValidationError this error commonly
    """

    def __init__(self, *args, **kwargs):
        """
        class intializer receive error messsage and status code from
        kwargs
        """
        self.status = kwargs.pop('status', status.HTTP_400_BAD_REQUEST)
        self.errors = kwargs.pop('errors', None)

    def get_body(self):
        """
        get the response body
        """
        return self.errors