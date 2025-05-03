from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC


@method_decorator(csrf_exempt, name='dispatch')
class PublicConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        key = request.data.get("key")
        print(f"🔐 Bestätigungs-Key erhalten: {key}")

        try:
            confirmation = EmailConfirmationHMAC.from_key(key)
            confirmation.confirm(request)
            return Response({"detail": "E-Mail erfolgreich bestätigt."})
        except Exception as e:
            print("❌ Fehler bei Bestätigung:", e)
            return Response({"detail": "Ungültiger oder abgelaufener Schlüssel."}, status=400)
