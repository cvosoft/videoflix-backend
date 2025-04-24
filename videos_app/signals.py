from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('abgespeicher!T')
    if created:
        print('ganz neu!')
