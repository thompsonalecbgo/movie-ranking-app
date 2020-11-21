from rest_framework import serializers

from .models import TopMovies, Movie

class TopMoviesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TopMovies
        fields = ['id']

class MovieSerializer(serializers.ModelSerializer):

    top_movies = TopMoviesSerializer(required=False)

    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'release_date',
                  'poster_path', 'top_movies']
    
    def create(self, validated_data):
        return Movie.objects.create(**validated_data)
