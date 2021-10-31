import http

from films.models import Films, Review, Vote
from films.serializers.review_serializer import ReviewSerializer, ReviewEditSerializer
from movies.generics.permission import has_permission
from movies.generics.views import APIView


class ReviewManagement(APIView):

    @has_permission
    def add_review(self, request, movie_id):
        """
        To add review on a particular movie
        :param request:
        :param movie_id:
        :return:
        """
        try:
            film_obj = Films.objects.get(id=movie_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)
        request_data = request.data
        request_data.update({"film": film_obj.id, 'user': request.user.id})
        serializer_obj = ReviewSerializer(data=request_data)
        if serializer_obj.is_valid():
            serializer_obj.save()
            return self.get_response(data=serializer_obj.data, message="Review Added successfully")
        else:
            return self.get_response(errors=serializer_obj.errors, statuscode=http.HTTPStatus.BAD_REQUEST)



    @has_permission
    def edit_review(self, request, review_id):
        """
        To edit the particualr review
        :param request:
        :param review_id:
        :return:
        """
        try:
            review_obj = Review.objects.get(id=review_id, user=request.user)
        except Films.DoesNotExist:
            return self.get_response(errors="Review Does Not Exists", message="Invalid Review Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)
        request_data = request.data.get("reviews")
        serializer_obj = ReviewEditSerializer(data={"reviews": request_data})
        if serializer_obj.is_valid():
            serializer_obj.update(review_obj, serializer_obj.data)
            return self.get_response(data=serializer_obj.data, message="Review Edited successfully")
        else:
            return self.get_response(errors=serializer_obj.errors, statuscode=http.HTTPStatus.BAD_REQUEST)

    @has_permission
    def list_reviews(self, request, movie_id):
        """
        To list the reviews on a particular movie
        :param request:
        :param movie_id:
        :return:
        """
        try:
            film_obj = Films.objects.get(id=movie_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)
        return self.get_response(
            data=ReviewSerializer(
                Review.objects.filter(film=film_obj), many=True
            ).data
        )

    @has_permission
    def delete_review(self, request, review_id):
        """
        To delete a particular Review
        :param request:
        :param review_id:
        :return:
        """
        try:
            review_obj = Review.objects.get(id=review_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Review Does Not Exists", message="Invalid Review Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)

        if review_obj.user != request.user:
            return self.get_response(errors="You dont have permission to delete this review", statuscode=http.HTTPStatus.BAD_REQUEST)

        review_obj.delete()
        return self.get_response(message="Review Deleted Successfully",
                                 statuscode=http.HTTPStatus.BAD_REQUEST)

    @has_permission
    def vote_movie(self, request, movie_id):
        """
        To UP Vote or Down Vote a Movie
        :param request:
        :param movie_id:
        :return:
        """
        try:
            film_obj = Films.objects.get(id=movie_id)
        except Films.DoesNotExist:
            return self.get_response(errors="Movie Does Not Exists", message="Invalid Movie Id",
                                     statuscode=http.HTTPStatus.BAD_REQUEST)
        if film_obj.is_voted is False:
            film_obj.is_voted = True
            film_obj.save()
        Vote.objects.update_or_create(**{'user':request.user, 'film': film_obj}, defaults=request.data)
        return self.get_response(message="Success")