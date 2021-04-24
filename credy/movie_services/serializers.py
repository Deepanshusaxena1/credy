import requests
from django.contrib.auth.models import User
from rest_framework.serializers import *
from django.conf import settings

from .models import Collection, Movie


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class Register(ModelSerializer):
    access_token = SerializerMethodField('get_token')

    def get_token(self, deep):
        req = requests.post(settings.TOKEN_API, data={'username': self.validated_data['username'],
                                                      'password': self.validated_data['password']})
        return req.json()['access']

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'access_token']
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }

    def save(self):
        user = User(
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'genres', 'uuid']


class CollectionSerializer(ModelSerializer):
    movies = MovieSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['title', 'uuid', 'description', 'movies', 'user']
        extra_kwargs = {
            'user': {'write_only': True},
        }

    def create(self, validated):
        movie_d = validated.pop('movies')
        _collection = Collection.objects.create(**validated)
        for unit_movie in movie_d:
            if Movie.objects.filter(uuid=unit_movie['uuid']).exists():
                raise ValidationError({"movies": [{"uuid": ["movie with this uuid already exists."]}]})
            else:
                m = Movie.objects.create(**unit_movie)
                _collection.movies.add(m)
        return _collection

    def update(self, instance, validated_data):
        movie_data = validated_data.pop('movies')
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        common_movies = []
        for movie in movie_data:
            if Movie.objects.filter(uuid=movie['uuid']).exists():
                _movie = Movie.objects.get(uuid=movie['uuid'])
                _movie.title = movie.get('title', _movie.title)
                _movie.description = movie.get('description', _movie.description)
                _movie.genres = movie.get('genres', _movie.genres)
                _movie.save()
                common_movies.append(_movie.uuid)
            else:
                _movie = Movie.objects.create(**movie)
                common_movies.append(_movie.uuid)
                instance.movies.add(_movie)
        for movie in instance.movies.all():
            if movie.uuid not in common_movies:
                instance.movies.remove(movie)
        instance.save()
        return instance
