# videoflix/serializers.py
from dj_rest_auth.serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from django.conf import settings
from importlib import import_module


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        print(">>> CustomPasswordResetSerializer aktiv!")  # Debug!
        generator_path = settings.DJ_REST_AUTH['PASSWORD_RESET_URL_GENERATOR']
        module_path, func_name = generator_path.rsplit('.', 1)
        module = import_module(module_path)
        url_generator = getattr(module, func_name)

        return {
            'url_generator': url_generator,
        }


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def validate(self, attrs):
        print("✅ CustomPasswordResetConfirmSerializer aktiv!")
        return super().validate(attrs)
