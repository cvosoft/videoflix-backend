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
from django.db import transaction


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        # queue = django_rq.get_queue('default')
        # queue.enqueue(convert_video_task, instance.id)

        #convert_video_task.delay(instance.id) - besser:
        transaction.on_commit(lambda: convert_video_task.delay(instance.id))


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        master_path = Path(instance.video_file.path)
        hls_directory = master_path.parent
        media_root = Path(settings.MEDIA_ROOT).resolve()
        videos_root = media_root / 'videos'  # Passe das ggf. an

        try:
            # Stelle sicher:
            # - hls_directory existiert
            # - hls_directory ist ein Unterverzeichnis von videos_root
            # - hls_directory ist nicht das gleiche wie videos_root
            if (
                hls_directory.exists() and
                hls_directory.is_dir() and
                videos_root in hls_directory.parents and
                hls_directory != videos_root
            ):
                shutil.rmtree(hls_directory)
                print(f"✅ HLS-Verzeichnis gelöscht: {hls_directory}")
            else:
                print(f"⚠️ Sicheres Löschen abgebrochen: {hls_directory}")
        except Exception as e:
            print(f"❌ Fehler beim Löschen des Verzeichnisses: {e}")

        # Original .mp4 löschen
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

    # Thumbnail löschen
    if instance.thumbnail_file:
        try:
            thumb_path = Path(instance.thumbnail_file.path)
            if thumb_path.exists():
                thumb_path.unlink()
                print(f"✅ Thumbnail gelöscht: {thumb_path}")
            else:
                print(f"⚠️ Thumbnail nicht gefunden: {thumb_path}")
        except Exception as e:
            print(f"❌ Fehler beim Löschen des Thumbnails: {e}")
