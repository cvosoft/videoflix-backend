from .models import Video
from .tasks import convert_to_height_pixels, convert_video_to_hls
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
import shutil
from pathlib import Path


# # Es werden verschiedene Auflösungen (120p, 360p, 720p, 1080p) zur manuellen Auswahl angeboten.
# @receiver(post_save, sender=Video)
# def video_post_save(sender, instance, created, **kwargs):
#     print('abgespeicher!T')
#     if created:
#         print('Neues Video erstellt')
#         for res in ['120', '360', '720', '1080']:
#             convert_to_height_pixels(instance.video_file.path, res)

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        base_output_dir = instance.video_file.path.replace('.mp4', '')
        master_path = convert_video_to_hls(
            instance.video_file.path, base_output_dir)
        # Pfad relativ zu MEDIA_ROOT setzen
        relative = Path(master_path).relative_to(
            Path(instance.video_file.storage.location))
        instance.video_file.name = str(relative)
        instance.save(update_fields=["video_file"])


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        master_path = Path(instance.video_file.path)
        hls_directory = master_path.parent

        # 1. HLS-Verzeichnis löschen
        if hls_directory.exists() and hls_directory.is_dir():
            try:
                shutil.rmtree(hls_directory)
                print(f"✅ HLS-Verzeichnis gelöscht: {hls_directory}")
            except Exception as e:
                print(f"❌ Fehler beim Löschen des Verzeichnisses: {e}")
        else:
            print(f"⚠️ Verzeichnis nicht gefunden: {hls_directory}")

        # 2. Original hochgeladene Datei löschen (falls noch da)
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
