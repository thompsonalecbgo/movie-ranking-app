from django.forms.models import model_to_dict
from rest_framework import serializers

from .models import TopMovies, Movie

class MovieRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        return model_to_dict(value)

class TopMoviesSerializer(serializers.ModelSerializer):
    
    movie = MovieRelatedField(many=True, read_only=True)

    class Meta:
        model = TopMovies
        fields = ['id', 'movie', 'title']

class MovieSerializer(serializers.ModelSerializer):

    top_movies = TopMoviesSerializer(required=False)

    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'release_date',
                  'poster_path', 'top_movies', 'rank']
    
    def create(self, validated_data):
        return Movie.objects.create_movie(**validated_data)
