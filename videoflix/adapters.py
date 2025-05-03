from allauth.account.adapter import DefaultAccountAdapter
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"http://127.0.0.1:4200/confirm-email/{emailconfirmation.key}/"

    def get_password_reset_url(self, user, token):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return f"http://127.0.0.1:4200/reset-password/{uid}/{token}/"


def my_password_reset_url_generator(request, user, token):
    print(">>> Custom password reset URL generator wurde aufgerufen!")
    adapter = MyAccountAdapter()
    return adapter.get_password_reset_url(user, token)
