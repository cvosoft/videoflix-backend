# views.py
from rest_framework import viewsets
from videos_app.models import Video, VideoSeries
from .serializers import SerieSerializer, PredigtSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class SerieViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = VideoSeries.objects.all()
    serializer_class = SerieSerializer

class PredigtViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Video.objects.all()
    serializer_class = PredigtSerializer
