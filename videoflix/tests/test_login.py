from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import mail
import re


class LoginTests(APITestCase):

    def setUp(self):

        self.email = "testuser@example.com"
        self.password = "OldPassword123!"

        url = reverse('authemail-signup')

        data = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 👇 E-Mail abfangen
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # 👇 Code per Regex extrahieren
        match = re.search(r'code[=: ]+(\w+)', email_body, re.IGNORECASE)
        self.assertIsNotNone(
            match, "Kein Verification Code in E-Mail gefunden")
        self.verification_code = match.group(1)

    def test_login_success(self):

        # verify first
        # 👇 Bestätigungsrequest absenden
        url = reverse('authemail-signup-verify')
        response = self.client.get(url, {
            "email": self.email,
            "code": self.verification_code
        }, format="json")
        self.assertEqual(response.status_code, 200)

        url = reverse('authemail-login')
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(url, data, format="json")

        # print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_not_verified(self):

        url = reverse('authemail-login')
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
