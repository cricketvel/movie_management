from rest_framework import serializers

from films.models import Films
from films.serializers.review_serializer import ReviewSerializer
from movies.generics.base_serializer import BaseModelSerializer


class MovieSerializer(BaseModelSerializer):

    created_by = serializers.CharField(required=False)
    up_count = serializers.IntegerField(required=False, read_only=True)
    down_count = serializers.IntegerField(required=False, read_only=True)
    review_count = serializers.IntegerField(required=False, read_only=True)
    review = ReviewSerializer(source='review_set', read_only=True, many=True)

    def validate(self, attrs):
        attrs["created_by"] = self.request.user
        return attrs


    class Meta:
        model = Films
        fields = "__all__"

class MovieEditSerializer(BaseModelSerializer):

    movie_name = serializers.CharField(required=False)
    genre = serializers.CharField(required=False)
    release_date = serializers.DateTimeField(required=False)


    class Meta:
        model = Films
        exclude = ("created_on", "created_by", "updated_on")

