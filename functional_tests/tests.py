import time

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

driver = r"D:\PROJECTS\geckodriver\geckodriver.exe"

url = "http://localhost:3000"

class NewUserTests(LiveServerTestCase):

    port = 8000

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = WebDriver(executable_path=driver)
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_can_connect_to_frontend(self):
        self.browser.get(url)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Welcome to My Top 100 Movies.", page_text)