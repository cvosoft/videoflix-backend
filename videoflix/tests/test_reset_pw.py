# tests/test_password_reset.py

from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
import re
from rest_framework import status




class PasswordResetTestCase(APITestCase):

    # user erstellen und verify
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

        # print(email_body)

        # 👇 Code per Regex extrahieren
        match = re.search(r'code[=: ]+(\w+)', email_body, re.IGNORECASE)
        self.assertIsNotNone(
            match, "Kein Verification Code in E-Mail gefunden")
        self.verification_code = match.group(1)

        # verify first
        # 👇 Bestätigungsrequest absenden
        url = reverse('authemail-signup-verify')
        response = self.client.get(url, {
            "email": self.email,
            "code": self.verification_code
        }, format="json")
        self.assertEqual(response.status_code, 200)

        # ✨ Outbox leeren für spätere Prüfung
        mail.outbox = []

    def test_password_reset_flow(self):

        url = reverse('authemail-password-reset')
        response = self.client.post(url, {
            "email": self.email,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # email abfangen
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # 👇 Code per Regex extrahieren
        match = re.search(r'code[=: ]+(\w+)', email_body, re.IGNORECASE)
        self.assertIsNotNone(
            match, "Kein Verification Code in E-Mail gefunden")
        self.verification_code = match.group(1)

        # nochmal verify machen
        url = reverse('authemail-password-reset-verified')

        new_password = "sdgz42ffefqa"

        response = self.client.post(url, {
            "code": self.verification_code,
            "password": new_password
        }, format="json")

        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # login with new password
        url = reverse('authemail-login')
        data = {
            "email": self.email,
            "password": new_password,
        }
        response = self.client.post(url, data, format="json")

        # print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
