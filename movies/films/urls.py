from django.urls import path, include

from films.viewsets.movie_management import MovieManagement
from films.viewsets.review_management import ReviewManagement

urlpatterns = [
    path('add', MovieManagement.as_view({"post": "add_movie"})),
    path('edit/<int:movie_id>', MovieManagement.as_view({"put": "edit_movie"})),
    path('list/movies', MovieManagement.as_view({"get": "list_all_movies"})),
    path('get/<int:movie_id>', MovieManagement.as_view({"get": "get_movie_detail"})),
    path('delete/<int:movie_id>', MovieManagement.as_view({"delete": "get_movie_detail"})),
    path('favourite/<int:movie_id>', MovieManagement.as_view({"post": "user_favorites"})),
    path('get/recommendation', MovieManagement.as_view({'get': 'get_recommendations'})),

    path('add/review/<int:movie_id>', ReviewManagement.as_view({"post": "add_review"})),
    path('edit/review/<int:review_id>', ReviewManagement.as_view({"put": "edit_review"})),
    path('list/reviews/<int:movie_id>', ReviewManagement.as_view({"get": "list_reviews"})),
    path('vote/<int:movie_id>', ReviewManagement.as_view({"post": "vote_movie"})),
    path('delete/review/<int:review_id>', ReviewManagement.as_view({"delete": "delete_review"})),

]