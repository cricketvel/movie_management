import http

from django.db.models import Count, Q, Case, When

from films.models import Films, UserFavourite
from films.serializers.movie_serializer import MovieSerializer, MovieEditSerializer
from movies.generics.permission import has_permission, has_admin_permission
from movies.generics.utils import request_sort_to_sort_dict
from movies.generics.views import APIView


class MovieManagement(APIView):

    @has_admin_permission
    def add_movie(self, request, *args, **kwargs):
        """
        To add movie data

        Only Super admin can add movies
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer_obj = MovieSerializer(request_obj=request, data=request.data)
        if serializer_obj.is_valid():
            serializer_obj.save()
            return self.get_response(data=serializer_obj.data, message="Movie Created Successfully")
        return self.get_response(errors=serializer_obj.errors, statuscode=http.HTTPStatus.BAD_REQUEST)

    @has_admin_permission
    def edit_movie(self, request, movie_id):
        """
        To edit a movie details
        :param request:
        :param movie_id:
        :return:
        """
        try:
            film_obj = Films.objects.get(id=movie_id, user=request.user)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id", statuscode=http.HTTPStatus.BAD_REQUEST)

        serializer_obj = MovieEditSerializer(request_obj=request, data=request.data)
        if serializer_obj.is_valid():
            serializer_obj.update(validated_data=serializer_obj.data, instance=film_obj)
            return self.get_response(data=serializer_obj.data, message="Movie Edited Successfully")
        return self.get_response(errors=serializer_obj.errors, statuscode=http.HTTPStatus.BAD_REQUEST)

    def list_all_movies(self, request, *args, **kwargs):
        """
        To list all movies.

        This is an open API which can be accessed by public users
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        film_obj = Films.objects.all().annotate(
            count=Count('vote__id'),
            review_count=Count('review__id'),
            up_count=Count(
                Case(
                    When(vote__is_up=True, then=1)
                )
            ),
            down_count=Count(
                Case(
                    When(vote__is_up=False, then=1)
                )
            )
        )
        sort_order = request_sort_to_sort_dict(request.GET, serializer=MovieSerializer)
        return self.get_response(data=MovieSerializer(film_obj.order_by(*sort_order), many=True).data)

    @has_permission
    def get_movie_detail(self, request, movie_id):
        """
        To get details of a particular movie
        :param request:
        :param movie_id:
        :return:
        """
        movie_data = MovieSerializer(Films.objects.filter(id=movie_id).annotate(
                review_count=Count('review__reviews'),
                up_count=Count(
                    Case(
                        When(vote__is_up=True, then=1)
                    )
                ),
                down_count=Count(
                    Case(
                        When(vote__is_up=False, then=1)
                    )
                )
            ), many=True).data

        if movie_data:
            return self.get_response(data=movie_data[0])
        else:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id", statuscode=http.HTTPStatus.BAD_REQUEST)

    @has_admin_permission
    def delete_movie(self, request, movie_id):
        """
        To delete a paricular movie
        :param request:
        :param movie_id:
        :return:
        """
        try:
            film_obj = Films.objects.get(id=movie_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)

        if film_obj.created_by != self.request.user:
            return self.get_response(errors="You dont have permission to Delete this Movie", statuscode=http.HTTPStatus.FORBIDDEN)

        film_obj.delete()
        return self.get_response(message="Movie Deleted Successfully")

    @has_permission
    def user_favorites(self, request, movie_id):
        """
        To choose a movie as a Favourite movie
        :param request:
        :param movie_id:
        :param is_favourite:
        :return:
        """
        is_favourite = request.data.get("is_favourite", False)
        try:
            film_obj = Films.objects.get(id=movie_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)
        if is_favourite is True:
            UserFavourite.objects.update_or_create(**{"user": self.request.user, "film": film_obj})
            return self.get_response(message="Movie Added to Favourites")
        else:
            UserFavourite.objects.filter(**{"user": self.request.user, "film": film_obj}).delete()
            return self.get_response(message="Movie Removed From Favourites")

    @has_permission
    def get_recommendations(self, request, *args, **kwargs):
        """
        TO return recommended list of movies
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        sort_order = request_sort_to_sort_dict(request.GET, serializer=MovieSerializer)
        data = UserFavourite.objects.filter(user=request.user).values_list('film__genre', flat=True).distinct()
        return self.get_response(
            data=MovieSerializer(
                Films.objects.filter(
                    genre__in=list(data)
                ).annotate(
                    review_count=Count('review__reviews'),
                    up_count=Count(
                        Case(
                            When(vote__is_up=True, then=1)
                        )
                    ),
                    down_count=Count(
                        Case(
                            When(vote__is_up=False, then=1)
                        )
                    )
                ).order_by(*sort_order), many=True).data
        )


