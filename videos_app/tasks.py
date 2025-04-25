import subprocess
from pathlib import Path


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
