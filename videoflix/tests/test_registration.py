from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class RegistrationTests(APITestCase):

    def test_registration_success(self):
        url = reverse('authemail-signup')

        data = {
            "email": "example@mail.de",
            "password": "examplePassword",
        }
        response = self.client.post(url, data, format="json")

        #print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_registration_invalid_data(self):
        url = reverse('authemail-signup')
        data = {
            "username": "",
            "email": "sdffdsgds",
            "password": "pass",
            "repeated_password": "passwort123",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
