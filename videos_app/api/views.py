# views.py
from rest_framework import viewsets
from videos_app.models import Video, VideoSeries
from .serializers import SerieSerializer, PredigtSerializer
from rest_framework.permissions import AllowAny


class SerieViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # 👈 das erlaubt öffentlichen Zugriff
    queryset = VideoSeries.objects.all()
    serializer_class = SerieSerializer


class PredigtViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = PredigtSerializer
