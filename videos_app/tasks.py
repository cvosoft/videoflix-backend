import subprocess
import logging
from pathlib import Path

import ffmpeg
from celery import shared_task
from .models import Video

logger = logging.getLogger(__name__)


@shared_task
def convert_video_task(video_id: int):
    logger.info("🎬 Starte ffmpeg-Konvertierung")
    instance = Video.objects.get(id=video_id)
    original_path = Path(instance.video_file.path)
    logger.debug(f"Eingabedatei: {original_path}")

    output_dir = original_path.with_suffix('')  # Pfad ohne .mp4
    master_path = convert_video_to_hls(original_path, output_dir)

    relative = master_path.relative_to(instance.video_file.storage.location)
    instance.video_file.name = str(relative)
    instance.save(update_fields=["video_file"])


def convert_video_to_hls(source_path: Path, output_dir: Path) -> Path:
    logger.info(f"🔧 Konvertiere Video: {source_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    probe = ffmpeg.probe(str(source_path))
    audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']

    _convert_video_resolutions(source_path, output_dir)
    audio_paths = _extract_audio_streams(
        source_path, output_dir, len(audio_streams))

    master_path = _generate_master_playlist(output_dir, audio_paths)
    return master_path


def _convert_video_resolutions(source: Path, output_dir: Path):
    resolutions = {
        '120p': '160x120',
        '360p': '640x360',
        '720p': '1280x720',
        '1080p': '1920x1080'
    }

    for label, res in resolutions.items():
        out_path = output_dir / f'video_{label}'
        out_path.mkdir(exist_ok=True)
        cmd = [
            'ffmpeg', '-i', str(source),
            '-vf', f'scale={res}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(out_path / f'{label}_%03d.ts'),
            '-an',  # Kein Audio in Video-Streams
            str(out_path / 'video.m3u8')
        ]
        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, timeout=3600)
            logger.debug(f"✅ {label} konvertiert.")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"❌ FFmpeg Fehler bei {label}:\n{e.stderr}", exc_info=True)
            raise
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ FFmpeg Timeout bei {label}", exc_info=True)
            raise


def _extract_audio_streams(source: Path, output_dir: Path, audio_count: int) -> list[tuple[str, str]]:
    audio_definitions = [
        ('de', 0),
        ('en', 1)
    ]
    audio_paths = []

    for lang, index in audio_definitions:
        if index >= audio_count:
            continue
        lang_dir = output_dir / f'audio_{lang}'
        lang_dir.mkdir(exist_ok=True)
        try:
            subprocess.run([
                'ffmpeg', '-i', str(
                    source), '-map', f'0:a:{index}', '-c:a', 'aac',
                '-b:a', '128k', '-f', 'hls', '-hls_time', '6', '-hls_playlist_type', 'vod',
                '-hls_segment_filename', str(lang_dir / f'{lang}_%03d.ts'),
                str(lang_dir / 'audio.m3u8')
            ], check=True, capture_output=True, text=True)
            audio_paths.append((lang, f'audio_{lang}/audio.m3u8'))
            logger.debug(f"🔊 Audio-Stream {lang} extrahiert")
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"⚠️ Fehler beim Extrahieren von Audio {lang}: {e.stderr}", exc_info=True)
    return audio_paths


def _generate_master_playlist(output_dir: Path, audio_paths: list[tuple[str, str]]) -> Path:
    master_path = output_dir / 'master.m3u8'
    resolutions = {
        '120p': '160x120',
        '360p': '640x360',
        '720p': '1280x720',
        '1080p': '1920x1080'
    }

    with master_path.open('w') as f:
        f.write('#EXTM3U\n\n')
        for code, path in audio_paths:
            f.write(
                f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{code.upper()}",'
                f'LANGUAGE="{code}",DEFAULT={"YES" if code == "de" else "NO"},AUTOSELECT=YES,'
                f'URI="{path}"\n'
            )
        for label, res in resolutions.items():
            f.write(
                f'#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION={res},CODECS="avc1.64001f",AUDIO="audio"\n'
            )
            f.write(f'video_{label}/video.m3u8\n')
    logger.info(f"📄 Master-Playlist erstellt: {master_path}")
    return master_path
