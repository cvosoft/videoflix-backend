from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny


class CustomLoginView(APIView):
    """
    Überschreibt die LoginView von django-rest-authemail,
    um keine Hinweise auf nicht verifizierte Accounts zu geben.
    """

    permission_classes = [AllowAny]  # ← Wichtig!

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        # Einheitliche Antwort bei Fehler
        if not user or not user.is_active or not user.is_verified:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Wenn alles passt → Token zurückgeben
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
