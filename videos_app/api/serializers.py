# serializers.py

from rest_framework import serializers
from videos_app.models import Video, VideoSeries


class PredigtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class SerieSerializer(serializers.ModelSerializer):
    predigten = PredigtSerializer(many=True, read_only=True)

    class Meta:
        model = VideoSeries
        fields = ['id', 'title', 'description', 'predigten']
