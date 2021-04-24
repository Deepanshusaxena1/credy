from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from collections import Counter


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.CharField(max_length=255)
    uuid = models.UUIDField(primary_key=True, )

    def __str__(self):
        return self.title

    def get_genres_list(self):
        genre_list = []
        genre_list = self.genres.split(',')
        return genre_list


class Collection(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True)
    description = models.TextField()
    movies = models.ManyToManyField('movie', related_name='collection_movies')

    def __str__(self):
        return str(self.uuid)

    def get_genres(self):
        genres = []
        for movie in self.movies.all():
            genres.extend(movie.get_genres_list())
        return genres

    @staticmethod
    def get_collection_genres(collections):
        genres = []
        for collection in collections:
            genres.extend(collection.get_genres())
        return list((dict(Counter(genres).most_common(3))).keys())
