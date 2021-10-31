
from rest_framework import serializers


class BaseSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request_obj', None)
        super(BaseSerializer, self).__init__(*args, **kwargs)

class BaseModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request_obj', None)
        super(BaseModelSerializer, self).__init__(*args, **kwargs)