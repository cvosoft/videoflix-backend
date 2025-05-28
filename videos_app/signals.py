import shutil
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.db import transaction

from .models import Video
from .tasks import convert_video_task



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        transaction.on_commit(lambda: convert_video_task.delay(instance.id))


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        _delete_hls_directory(instance.video_file)
        _delete_original_file(instance.video_file)


def _delete_hls_directory(video_file):
    master_path = Path(video_file.path)
    hls_directory = master_path.parent
    media_root = Path(settings.MEDIA_ROOT).resolve()
    videos_root = media_root / 'videos'

    try:
        if (
            hls_directory.exists()
            and hls_directory.is_dir()
            and videos_root in hls_directory.parents
            and hls_directory != videos_root
        ):
            shutil.rmtree(hls_directory)
            logger.info(f"HLS-Verzeichnis gelöscht: {hls_directory}")
        else:
            logger.info(f"Sicheres Löschen abgebrochen: {hls_directory}")
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Verzeichnisses: {e}")


def _delete_original_file(video_file):
    original_file_path = video_file.storage.path(
        video_file.name.replace('/master.m3u8', '.mp4')
    )
    original_file = Path(original_file_path)

    if original_file.exists():
        try:
            original_file.unlink()
            logger.info(f"Original-Datei gelöscht: {original_file}")
        except Exception as e:
            logger.info(f"Fehler beim Löschen der Originaldatei: {e}")
    else:
        logger.error(f"Original-Datei nicht gefunden: {original_file}")
