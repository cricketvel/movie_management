from django.contrib.auth import authenticate

from rest_framework import serializers

from movies.generics.error_class import ValidationError

from users.models import CustomUser
from movies.generics.base_serializer import BaseModelSerializer

class LoginSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(LoginSerializer, self).__init__(*args, **kwargs)


    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    is_superuser = serializers.BooleanField(required=False)
    id = serializers.IntegerField(required=False)

    def validate(self, data):

        email = data.get('email', None)
        password = data.get('password', None)


        if email is None:
            raise ValidationError(
                'An email address is required to log in.'
            )


        if password is None:
            raise ValidationError({
                "Password is Required",
            })


        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist as exc:

            user_obj = None

        if user_obj is None:
            raise ValidationError(
                'User not found'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise ValidationError(
                'Invalid Email/Password'
            )

        if not user.is_active:
            raise ValidationError(
                'This user has been deactivated.Please contact your company administrator'
            )


        return {
            'email': user.email,
            'username': user.username,
            'token': user.token,
            'is_superuser': user.is_superuser,
            'role': user.role,
            'id': user.id
        }

class UserSerializer(BaseModelSerializer):

    class Meta:
        model = CustomUser
        fields = "__all__"