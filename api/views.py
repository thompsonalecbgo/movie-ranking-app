from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TopMovies, Movie
from .serializers import TopMoviesSerializer, MovieSerializer

# Create your views here.
class TopMoviesViewSet(viewsets.ModelViewSet):

    queryset = TopMovies.objects.all()
    serializer_class = TopMoviesSerializer

    @action(detail=False, methods=["post"])
    def new(self, request):
        new_top_movies = TopMovies.objects.create()
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(top_movies=new_top_movies)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        top_movies = self.get_object()
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(top_movies=top_movies)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieViewSet(viewsets.ModelViewSet):

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    @action(detail=True, methods=["delete"], url_path="delete-rank")
    def delete_rank(self, request, pk=None):
        movie = self.get_object()
        movie.delete_rank()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"], url_path="move-rank-up")
    def move_rank_up(self, request, pk=None):
        movie = self.get_object()
        current_rank = movie.rank
        movie.reorder_rank(current_rank-1)
        serializer = self.get_serializer(movie)
        return Response(serializer.data)
    
    @action(detail=True, methods=["put"], url_path="move-rank-down")
    def move_rank_down(self, request, pk=None):
        movie = self.get_object()
        current_rank = movie.rank
        movie.reorder_rank(current_rank+1)
        serializer = self.get_serializer(movie)
        return Response(serializer.data)