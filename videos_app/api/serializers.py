# serializers.py

from rest_framework import serializers
from videos_app.models import Video, VideoSeries


class PredigtSerializer(serializers.ModelSerializer):
    serie_title = serializers.CharField(source='serie.title', read_only=True)

    class Meta:
        model = Video
        fields = '__all__'


class SerieSerializer(serializers.ModelSerializer):
    predigten = PredigtSerializer(many=True, read_only=True)

    class Meta:
        model = VideoSeries
        fields = ['id', 'title', 'description', 'predigten']
