import json

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import TopMovies, Movie

API_PATH = 'api/v1'

TEST_MOVIES = json.load(open("functional_tests/movies.json"))

class APIRootTest(TestCase):
    
    client = APIClient
    
    def test_api_root_correct_status_code(self):
        response = self.client.get(f'/{API_PATH}/')
        self.assertEqual(response.status_code, 200)

class TopMoviesViewSetTest(TestCase):
    
    client = APIClient
    
    def test_can_GET_top_movies(self):
        top_movies = TopMovies.objects.create()
        response = self.client.get(f'/{API_PATH}/top-movies/{top_movies.id}/')
        self.assertEqual(response.status_code, 200)

class MovieViewSetTest(TestCase):
    
    client = APIClient
    
    def setUp(self):
        top_movies = TopMovies.objects.create()
        movie = {
            'tmdb_id': '123',
            'title': 'new movie',
            'release_date': '2012-04-25',
            'poster_path': 'https://themoviedb.org/path-to-movie-poster.jpg',
            'top_movies': top_movies
        }
        self.movie = Movie.objects.create(**movie)

    def test_can_GET_movie(self):
        response = self.client.get(f'/{API_PATH}/top-movie/{self.movie.id}/')
        self.assertEqual(response.status_code, 200)

    def test_can_DELETE_movie(self):
        response = self.client.delete(f'/{API_PATH}/top-movie/{self.movie.id}/')
        self.assertEqual(response.status_code, 204)

class TopMoviesTest(TestCase):
    
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

class MovieTest(TestCase):
    
    client = APIClient
    
    def test_can_POST_new_movie_to_existing_list(self):
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

class MovieRankingTest(TestCase):

    client = APIClient

    def setUp(self):
        self.top_movies = TopMovies.objects.create()
        self.movies = [
            self.client.post(
                f'/{API_PATH}/top-movies/{self.top_movies.id}/add/',
                data=movie
            ).data
            for movie in TEST_MOVIES
        ]
        self.other_top_movies = TopMovies.objects.create()
        self.reversed_movies = [
            self.client.post(
                f'/{API_PATH}/top-movies/{self.other_top_movies.id}/add/',
                data=movie
            ).data
            for movie in reversed(TEST_MOVIES)
        ]

    def test_added_movie_increments_rank_correctly(self):
        for i, movie in enumerate(self.movies):
            self.assertEqual(movie["rank"], i+1)
            self.assertEqual(movie["title"], TEST_MOVIES[i]["title"])
    
        for i, movie in enumerate(self.reversed_movies):
            self.assertEqual(movie["rank"], i+1)
            self.assertEqual(movie["title"], TEST_MOVIES[-(i+1)]["title"])

    def test_cannot_add_same_movie_in_same_top_movies_twice(self):
        self.client.post(
            f'/{API_PATH}/top-movies/{self.top_movies.id}/add/',
            data=TEST_MOVIES[0]
        )
        self.assertEqual(self.top_movies.movie.count(), 5)
    
    def test_delete_movie_updates_movie_ranks_correctly(self):
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[1]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[2]["title"])

        response = self.client.delete(
            f'/{API_PATH}/top-movie/{movie_2.id}/delete-rank/',
        )
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.top_movies.movie.count(), 4)
        
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[2]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[3]["title"])

    def test_move_rank_up_updates_movie_ranks_correctly(self):
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[1]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[2]["title"])

        response = self.client.put(
            f'/{API_PATH}/top-movie/{movie_2.id}/move-rank-up/',
        )
        
        self.assertEqual(response.data["rank"], 1)
        self.assertEqual(self.top_movies.movie.count(), 5)
        
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[1]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[2]["title"])

    def test_move_rank_down_updates_movie_ranks_correctly(self):
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[1]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[2]["title"])

        response = self.client.put(
            f'/{API_PATH}/top-movie/{movie_2.id}/move-rank-down/',
        )
        
        self.assertEqual(response.data["rank"], 3)
        self.assertEqual(self.top_movies.movie.count(), 5)
        
        movie_1 = self.top_movies.movie.get(rank=1)
        movie_2 = self.top_movies.movie.get(rank=2)
        movie_3 = self.top_movies.movie.get(rank=3)
        
        self.assertEqual(movie_1.title, TEST_MOVIES[0]["title"])
        self.assertEqual(movie_2.title, TEST_MOVIES[2]["title"])
        self.assertEqual(movie_3.title, TEST_MOVIES[1]["title"])

