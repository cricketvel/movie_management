from users.models import CustomUser
from users.serializers.login_serializer import LoginSerializer, UserSerializer
from rest_framework import status


from movies.generics.views import APIView


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def login(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, request=request)
        serializer.is_valid(raise_exception=True)
        return self.get_response(data=serializer.data, statuscode=status.HTTP_200_OK, message="Login Successful")


class Register(APIView):
    def register(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.get_response(message='User Registered Successfully')
        else:
            return self.get_response(message=serializer.errors)