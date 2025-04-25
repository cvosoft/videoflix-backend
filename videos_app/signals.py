from .models import Video
from .tasks import convert_to_height_pixels
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from pathlib import Path


# Es werden verschiedene Auflösungen (120p, 360p, 720p, 1080p) zur manuellen Auswahl angeboten.
@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('abgespeicher!T')
    if created:
        print('Neues Video erstellt')
        for res in ['120', '360', '720', '1080']:
            convert_to_height_pixels(instance.video_file.path, res)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        # Original-Datei löschen
        original_path = Path(instance.video_file.path)
        if original_path.is_file():
            original_path.unlink()
            print('Original gelöscht')
        else:
            print('Original nicht gefunden')

        # erstellte löschen
        for res in ['120', '360', '720', '1080']:
            converted_path = original_path.with_name(
                f"{original_path.stem}_{res}p.mp4")

            if converted_path.is_file():
                converted_path.unlink()
                print(f'{res} Version gelöscht')
            else:
                print(f'{res} Version nicht gefunden')
