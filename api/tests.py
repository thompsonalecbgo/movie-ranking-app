from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import TopMovies, Movie

API_PATH = 'api/v1'

# Create your tests here.
class APIRootTest(TestCase):
    client = APIClient
    def test_api_root_correct_status_code(self):
        response = self.client.get(f'/{API_PATH}/')
        self.assertEqual(response.status_code, 200)

# get movies
class TopMoviesViewSetTest(TestCase):
    client = APIClient
    def test_can_GET_top_movies(self):
        top_movies = TopMovies.objects.create()
        response = self.client.get(f'/{API_PATH}/top-movies/{top_movies.id}/')
        self.assertEqual(response.status_code, 200)

# post movies
class NewTopMoviesTest(TestCase):
    client = APIClient
    def test_can_POST_new_top_movies_list(self):
        response = self.client.post(
            f'/{API_PATH}/top-movies/new/',
            data={
                'tmdb_id': '123',
                'title': 'new movie',
                'release_date': '2012-04-25',
                'poster_path': 'https://themoviedb.org/path-to-movie-poster.jpg'
            })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TopMovies.objects.count(), 1)
        new_top_movies = TopMovies.objects.first()
        new_movie = new_top_movies.movie.first()
        self.assertEqual(new_movie.title, "new movie")

class NewTopMovieTest(TestCase):
    client = APIClient
    def test_can_POST_new_top_movie_to_existing_list(self):
        correct_list = TopMovies.objects.create()
        other_list = TopMovies.objects.create()

        self.client.post(
            f'/{API_PATH}/top-movies/{correct_list.id}/add/',
            data={
                'tmdb_id': '123',
                'title': 'new movie',
                'release_date': '2012-04-25',
                'poster_path': 'https://themoviedb.org/path-to-movie-poster.jpg'
            }
        )

        self.assertEqual(Movie.objects.count(), 1)
        new_movie = Movie.objects.first()
        self.assertEqual(new_movie.title, "new movie")
        self.assertEqual(new_movie.top_movies, correct_list)
        