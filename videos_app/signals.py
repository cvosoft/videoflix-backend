from .models import Video
from .tasks import *
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
import shutil
from pathlib import Path
from .tasks import convert_video_task
import django_rq
from django.conf import settings

# # Es werden verschiedene Auflösungen (120p, 360p, 720p, 1080p) zur manuellen Auswahl angeboten.
# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     print('abgespeicher!T')
#     if created:
#         print('Neues Video erstellt')
#         for res in ['120', '360', '720', '1080']:
#             convert_to_height_pixels(instance.video_file.path, res)

# ALT!
# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     if created and instance.video_file:
#         base_output_dir = instance.video_file.path.replace('.mp4', '')
#         master_path = convert_video_to_hls(
#             instance.video_file.path, base_output_dir)
#         # Pfad relativ zu MEDIA_ROOT setzen
#         relative = Path(master_path).relative_to(
#             Path(instance.video_file.storage.location))
#         instance.video_file.name = str(relative)
#         instance.save(update_fields=["video_file"])


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        # queue = django_rq.get_queue('default')
        # queue.enqueue(convert_video_task, instance.id)

        convert_video_task.delay(instance.id)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        master_path = Path(instance.video_file.path)

        # Nur löschen, wenn master.m3u8 in einem _eigenen_ Unterordner liegt
        hls_directory = master_path.parent
        media_root = Path(settings.MEDIA_ROOT).resolve()

        try:
            # Stelle sicher, dass der Pfad ein Unterverzeichnis von MEDIA_ROOT ist, aber nicht MEDIA_ROOT selbst
            if (
                hls_directory.exists() and
                hls_directory.is_dir() and
                media_root in hls_directory.parents and
                hls_directory != media_root
            ):
                shutil.rmtree(hls_directory)
                print(f"✅ HLS-Verzeichnis gelöscht: {hls_directory}")
            else:
                print(f"⚠️ Sicheres Löschen abgebrochen: {hls_directory}")
        except Exception as e:
            print(f"❌ Fehler beim Löschen des Verzeichnisses: {e}")

        # Original .mp4 löschen (wie bisher)
        original_file = Path(instance.video_file.storage.path(
            instance.video_file.name.replace('/master.m3u8', '.mp4')))
        if original_file.exists():
            try:
                original_file.unlink()
                print(f"✅ Original-Datei gelöscht: {original_file}")
            except Exception as e:
                print(f"❌ Fehler beim Löschen der Originaldatei: {e}")
        else:
            print(f"⚠️ Original-Datei nicht gefunden: {original_file}")
