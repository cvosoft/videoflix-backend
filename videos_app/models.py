from django.db import models
from datetime import date


class VideoSeries(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Video(models.Model):
    serie = models.ForeignKey(VideoSeries, related_name='predigten', on_delete=models.CASCADE, default=1)
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.serie.title} – {self.title}"