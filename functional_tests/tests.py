import time

from django.test import LiveServerTestCase
# from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchElementException

driver = r"D:\PROJECTS\geckodriver\geckodriver.exe"

url = "http://localhost:3000/"

TIME_LIMIT = 10

class NewUserTests(LiveServerTestCase):

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

    def test_can_connect_to_frontend(self):
        self.browser.get(url)
        welcome_message = self.wait_for_element(
            lambda: self.browser.find_element_by_id("welcome")
        ).text
        self.assertIn("Welcome to My Top 100 Movies.", welcome_message)

    def test_user_can_create_list(self):

        # user visits website Search Movie section
        self.browser.get(url + "search/")
        self.assertIn('Search Movie', self.browser.title)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Search Movie", page_text)

        # user searches for movie Titanic
        # search results show several options with Titanic in the title
        # user checks if the correct Titanic is in the options
        movie = 'Titanic'
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
        self.assertIn("Titanic (1997)", results)
        
        # user selects correct Titanic
        # system creates new list with movie Titanic
        result_idx = results.index("Titanic (1997)")
        search_results[result_idx].click()
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li")
        )
        movies = [movie.text for movie in top_movies]
        self.assertIn("Titanic (1997)", movies)
        self.assertEqual(len(movies), 1)

        # user searches for movie Cinderella
        movie = 'Cinderella'
        search_bar = self.browser.find_element_by_id("search-bar")
        search_bar.send_keys(movie)
        search_results = self.wait_for_element(
            lambda: self.browser.find_element_by_id("search-results")
        )
        search_results = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#search-results li")
        )
        results = [result.text for result in search_results]
        self.assertIn("Cinderella (2015)", results)
        
        # user selects correct Cinderella
        # system adds the selected movie to existing list
        result_idx = results.index("Cinderella (2015)")
        search_results[result_idx].click()
        top_movies = self.wait_for_element(
            lambda: self.browser.find_element_by_id("top-movies")
        )
        top_movies = self.wait_for_element(
            lambda: self.browser.find_elements_by_css_selector("#top-movies li")
        )
        movies = [movie.text for movie in top_movies]
        self.assertIn("Titanic (1997)", movies)
        self.assertIn("Cinderella (2015)", movies)
        self.assertEqual(len(movies), 2)

    def test_user_can_delete_movies_in_list(self):
        pass

    def test_user_can_reorder_rank_of_movies_in_list(self):
        pass

    def test_multiple_users_can_make_their_own_lists(self):
        pass