from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
class APIRootTest(TestCase):

    client = APIClient

    def test_status_code(self):
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)