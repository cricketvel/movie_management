from films.models import Review
from movies.generics.base_serializer import BaseModelSerializer


class ReviewSerializer(BaseModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"

class ReviewEditSerializer(BaseModelSerializer):

    class Meta:
        model = Review
        fields = ("reviews",)



