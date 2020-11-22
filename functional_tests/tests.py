import time
import json
from datetime import datetime

from django.test import LiveServerTestCase
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException

from api.models import TopMovies, Movie

driver = r"D:\PROJECTS\geckodriver\geckodriver.exe"

url = "http://localhost:3000/"

TIME_LIMIT = 10

TEST_MOVIES = json.load(open("functional_tests/movies.json"))

class SeleniumTests(LiveServerTestCase):

    port = 8000

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox(executable_path=driver)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
    
    def wait_for_element(self, callback):
        start_time = time.time()
        while True:
            try:
                element = callback()
                if element:
                    return element
            except (WebDriverException) as e:
                print(e)
                if time.time() - start_time > TIME_LIMIT:
                    raise e
                time.sleep(0.5)

# class ConnectionTests(SeleniumTests):

#     def test_frontend_can_connect_to_backend(self):
#         self.browser.get(url)
#         welcome_message = self.wait_for_element(
#             lambda: self.browser.find_element_by_id("welcome")
#         ).text
#         self.assertIn("Welcome to My Top 100 Movies.", welcome_message)

class NewUserTests(SeleniumTests):

    MOVIE_1 = 'Titanic'
    RESULT_1 = 'Titanic (1997)'
    MOVIE_2 = 'Cinderella'
    RESULT_2 = 'Cinderella (2015)'

    def search_movie_and_click_result(self, movie, result):
        search_bar = self.browser.find_element_by_id("search-bar")
        self.assertEqual(
            search_bar.get_attribute('placeholder'),
            'Search for your favorite movies!'
        )

        search_bar.send_keys(movie)
        search_results = self.wait_for_element(
            lambda: self.browser.find_element_by_id("search-results")
        )
        search_results = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#search-results li")
        )
        results = [result.text for result in search_results]
        self.assertIn(result, results)

        result_idx = results.index(result)
        search_results[result_idx].click()

    def check_if_movie_in_top_movies(self, movies, count):
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        top_movies = [movie.text for movie in top_movies]
        for movie in movies:
            self.assertIn(movie, top_movies)
        self.assertEqual(len(movies), count)

    def count_top_movie_lists(self, count):
        top_movie_lists = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movie-lists")
        )
        top_movie_lists = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movie-lists .top-movie-list")
        )
        self.assertEqual(len(top_movie_lists), count)

    def test_user_can_create_top_movies(self):

        # user visits website
        self.browser.get(url)
        self.assertIn('Top Movies', self.browser.title)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Search Movie", page_text)

        # user searches for movie Titanic
        # search results show several options with Titanic in the title
        # user checks if the correct Titanic is in the options
        # user selects correct Titanic
        # system creates new list with movie Titanic
        self.search_movie_and_click_result(self.MOVIE_1, self.RESULT_1)
        self.check_if_movie_in_top_movies([self.RESULT_1,], 1)

        # user searches for movie Cinderella
        # user selects correct Cinderella
        # system adds the selected movie to existing list
        self.search_movie_and_click_result(self.MOVIE_2, self.RESULT_2)
        self.check_if_movie_in_top_movies([self.RESULT_1, self.RESULT_2], 2)

    def test_user_can_create_multiple_top_movies(self):

        MOVIE_1 = 'Titanic'
        RESULT_1 = 'Titanic (1997)'
        MOVIE_2 = 'Cinderella'
        RESULT_2 = 'Cinderella (2015)'

        self.browser.get(url)
        self.search_movie_and_click_result(self.MOVIE_1, RESULT_1)
        self.check_if_movie_in_top_movies([self.RESULT_1,], 1)

        self.browser.get(url)
        self.count_top_movie_lists(1)
        self.search_movie_and_click_result(MOVIE_2, RESULT_2)
        self.check_if_movie_in_top_movies([self.RESULT_2,], 1)

        self.browser.get(url)
        self.count_top_movie_lists(2)

class TopMoviesFeaturesTests(SeleniumTests):

    def setUp(self):
        self.top_movies = TopMovies.objects.create()
        self.movies = [
            Movie.objects.create_movie(**movie, top_movies=self.top_movies)
            for movie in TEST_MOVIES
        ]

    def test_added_movies_are_rank_correctly(self):
        self.browser.get(url + f"top-movies/{self.top_movies.id}/")
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        movies = [movie.text for movie in top_movies]
        for i, movie in enumerate(self.movies):
            year = datetime.strptime(movie.release_date, "%Y-%m-%d").year
            self.assertEqual(f"{movie.title} ({year})", movies[i])
        movie_ranks = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-rank")
        )
        ranks = [rank.text for rank in movie_ranks]
        for i, rank in enumerate(ranks):
            self.assertEqual(int(rank), i+1)

    def test_user_can_move_movie_rank_up(self):
        self.browser.get(url + f"top-movies/{self.top_movies.id}/")
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        movies = [movie.text for movie in top_movies]

        # move rank of third movie up
        move_rank_btns = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .move-rank-up")
        )
        move_rank_btns[2].click()

        updated_top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        updated_movies = [movie.text for movie in updated_top_movies]

        self.assertEqual(movies[0], updated_movies[0])
        self.assertEqual(movies[1], updated_movies[2])
        self.assertEqual(movies[2], updated_movies[1])
        self.assertEqual(movies[3], updated_movies[3])
        self.assertEqual(movies[4], updated_movies[4])
    
    def test_user_can_move_movie_rank_down(self):
        self.browser.get(url + f"top-movies/{self.top_movies.id}/")
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        movies = [movie.text for movie in top_movies]

        # move rank of third movie up
        move_rank_btns = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .move-rank-down")
        )
        move_rank_btns[2].click()

        updated_top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        updated_movies = [movie.text for movie in updated_top_movies]

        self.assertEqual(movies[0], updated_movies[0])
        self.assertEqual(movies[1], updated_movies[1])
        self.assertEqual(movies[2], updated_movies[3])
        self.assertEqual(movies[3], updated_movies[2])
        self.assertEqual(movies[4], updated_movies[4])

    def test_user_can_delete_movies_in_list(self):
        self.browser.get(url + f"top-movies/{self.top_movies.id}/")
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        movies = [movie.text for movie in top_movies]

        # move rank of third movie up
        delete_rank_btns = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .delete-rank")
        )
        delete_rank_btns[2].click()

        updated_top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li .movie-detail")
        )
        updated_movies = [movie.text for movie in updated_top_movies]

        self.assertEqual(movies[0], updated_movies[0])
        self.assertEqual(movies[1], updated_movies[1])
        self.assertEqual(movies[3], updated_movies[2])
        self.assertEqual(movies[4], updated_movies[3])
        self.assertNotIn(movies[2], updated_movies)

# TODO:

def test_user_cannot_add_same_movie_in_same_top_movies_twice(self):
    pass

def test_can_change_top_movie_list_title(self):
    pass

def test_delete_top_movie_list(self):
    pass