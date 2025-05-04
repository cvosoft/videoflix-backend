# tests/test_password_reset.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from allauth.account.models import EmailAddress


class PasswordResetTestCase(TestCase):
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

        # 👇 Markiere E-Mail-Adresse als verifiziert
        EmailAddress.objects.create(
            user=self.user,
            email=self.email,
            verified=True,
            primary=True
        )

    def test_password_reset_flow(self):
        # 1. Simuliere Reset-Anfrage
        url = reverse('rest_password_reset')
        response = self.client.post(url, {
            "email": self.email
        })
        self.assertEqual(response.status_code, 200)

        print(response.status_code)

        # 2. Token & UID manuell generieren (wie Django es tun würde)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        print(uid, token)

        # 3. Setze neues Passwort über Confirm-Endpunkt
        new_password = "MyNewTestPass123!"
        url = reverse('rest_password_reset_confirm')
        response = self.client.post(url, {
            "uid": uid,
            "token": token,
            "new_password1": new_password,
            "new_password2": new_password
        })
        self.assertEqual(response.status_code, 200)

        # 4. Prüfe Login mit neuem Passwort
        url = reverse('rest_login')
        login_success = self.client.post(url, {
            "email": self.email,
            "password": new_password
        })
        self.assertEqual(login_success.status_code, 200)
