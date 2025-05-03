from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"http://127.0.0.1:4200/confirm-email/{emailconfirmation.key}/"