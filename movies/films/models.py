from django.db import models

# Create your models here.
from django.utils import timezone
from users.models import CustomUser


class Films(models.Model):
    movie_name = models.CharField(max_length=255, null=False, blank=False)
    genre = models.CharField(max_length=255, null=False, blank=False)
    release_date = models.DateTimeField(max_length=255, null=False, blank=True)
    is_voted = models.BooleanField(default=False)
    created_on = models.DateTimeField(editable=False)
    updated_on = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    REQUIRED_FIELDS = ['genre', 'movie_name', 'release_date']


    def save(self, *args, **kwargs):
        if not self.id:
            self.created_on = timezone.now()

        self.updated_on = timezone.now()
        return super(Films, self).save(*args, **kwargs)

    def __str__(self):
        return self.movie_name


class UserFavourite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    film = models.ForeignKey(Films, on_delete=models.CASCADE)


class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    film = models.ForeignKey(Films, on_delete=models.CASCADE)
    is_up = models.BooleanField()

    REQUIRED_FIELDS = ['is_up']

    class Meta:
        unique_together = ('user', 'film')


class Review(models.Model):
    reviews = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    film = models.ForeignKey(Films, on_delete=models.CASCADE)


