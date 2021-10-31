

from users.models import CustomUser
from movies.generics.base_serializer import BaseModelSerializer


class UserSerializer(BaseModelSerializer):

   class Meta:
        model = CustomUser
        exclude = ("password", "is_staff", "created_on", "updated_on", "is_confirmed", "groups", "user_permissions",
                   )

