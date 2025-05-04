from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model


class LoginTests(APITestCase):

    def setUp(self):
        self.User = get_user_model()
        self.email = "testuser@example.com"
        self.password = "OldPassword123!"
        self.user = self.User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            is_active=True  # wichtig!
        )

    def test_login_success(self):

        # 👇 Markiere E-Mail-Adresse als verifiziert
        EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            verified=True,
            primary=True
        )

        url = reverse('rest_login')
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(url, data, format="json")

        # print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_not_verified(self):

        url = reverse('rest_login')
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(url, data, format="json")


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)