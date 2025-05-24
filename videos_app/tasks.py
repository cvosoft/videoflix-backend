import subprocess
from pathlib import Path
import ffmpeg
import shutil
import os
from .models import Video
import logging
from celery import shared_task


# CELERY TASK!
@shared_task
def convert_video_task(video_id):
    logging.debug("🚀 Starte ffmpeg-Kommando")
    instance = Video.objects.get(id=video_id)
    original_path = instance.video_file.path
    logging.debug(f"📍 Eingabedatei: {original_path}")

    base_output_dir = original_path.replace('.mp4', '')

    master_path = convert_video_to_hls(original_path, base_output_dir)

    # Pfad relativ zu MEDIA_ROOT setzen
    relative = Path(master_path).relative_to(
        Path(instance.video_file.storage.location))
    instance.video_file.name = str(relative)
    instance.save(update_fields=["video_file"])


def convert_video_to_hls(source_path: str, output_dir: str):
    logging.debug(f"🎞 Starte Konvertierung für {source_path}")
    source = Path(source_path)
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    # 1. Streams analysieren
    probe = ffmpeg.probe(str(source))
    audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']

    has_two_audio = len(audio_streams) >= 2

    # 2. Erzeuge Video-Varianten
    resolutions = {
        '120p': '160x120',
        '360p': '640x360',
        '720p': '1280x720',
        '1080p': '1920x1080'
    }

    for label, res in resolutions.items():
        out_path = base_dir / f'video_{label}'
        out_path.mkdir(exist_ok=True)

        cmd = [
            'ffmpeg', '-i', str(source),
            '-vf', f'scale={res}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(out_path / f'{label}_%03d.ts'),
            '-an',
            str(out_path / 'video.m3u8')
        ]

        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, timeout=3600)
            if result.returncode != 0:
                print(f"❌ FFmpeg Fehler ({label}):", result.stderr)
                raise RuntimeError(f"Fehler bei {label}")
            else:
                print(f"✅ Erfolgreich {label} konvertiert.")
        except subprocess.TimeoutExpired:
            print(f"⏰ FFmpeg Timeout bei {label}")
            raise

    # 3. Extrahiere Audiospuren
    audio_paths = []
    if len(audio_streams) >= 1:
        de_path = base_dir / 'audio_de'
        de_path.mkdir(exist_ok=True)
        subprocess.run([
            'ffmpeg', '-i', str(source), '-map', '0:a:0', '-c:a', 'aac',
            '-b:a', '128k', '-f', 'hls', '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(de_path / 'de_%03d.ts'),
            str(de_path / 'audio.m3u8')
        ])
        audio_paths.append(('de', 'audio_de/audio.m3u8'))

    if len(audio_streams) >= 2:
        en_path = base_dir / 'audio_en'
        en_path.mkdir(exist_ok=True)
        subprocess.run([
            'ffmpeg', '-i', str(source), '-map', '0:a:1', '-c:a', 'aac',
            '-b:a', '128k', '-f', 'hls', '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(en_path / 'en_%03d.ts'),
            str(en_path / 'audio.m3u8')
        ])
        audio_paths.append(('en', 'audio_en/audio.m3u8'))

    # 4. Erstelle master.m3u8
    master_path = base_dir / 'master.m3u8'
    with open(master_path, 'w') as f:
        f.write('#EXTM3U\n\n')
        for code, path in audio_paths:
            f.write(
                f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{code.upper()}",LANGUAGE="{code}",DEFAULT={"YES" if code == "de" else "NO"},AUTOSELECT=YES,URI="{path}"\n')

        for label in resolutions.keys():
            f.write(
                f'#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION={resolutions[label]},CODECS="avc1.64001f",AUDIO="audio"\n')
            f.write(f'video_{label}/video.m3u8\n')

    return str(master_path)
