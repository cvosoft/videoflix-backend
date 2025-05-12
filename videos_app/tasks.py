import subprocess
from pathlib import Path
import ffmpeg
import shutil
import os


def convert_to_height_pixels(source, height_key):
    resolution_map = {
        '120': '160x120',
        '360': '640x360',
        '720': '1280x720',
        '1080': '1920x1080'
    }

    if height_key not in resolution_map:
        print(f"⚠️ Ungültige Auflösung: {height_key}")
        return

    resolution = resolution_map[height_key]
    p = Path(source)
    name = p.stem
    new_file_name = p.with_name(f"{name}_{height_key}p.mp4")

    cmd = [
        'ffmpeg',
        '-i', str(source),
        '-s', resolution,
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        str(new_file_name)
    ]

    run = subprocess.run(cmd, capture_output=True, text=True)

    if run.returncode != 0:
        print(f"❌ Fehler bei {height_key}p-Konvertierung:", run.stderr)
    else:
        print(f"✅ {height_key}p erstellt:", new_file_name)


def convert_video_to_hls(source_path: str, output_dir: str):
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
        subprocess.run([
            'ffmpeg', '-i', str(source),
            '-vf', f'scale={res}',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_segment_filename', str(out_path / f'{label}_%03d.ts'),
            '-an',
            str(out_path / 'video.m3u8')
        ])

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
