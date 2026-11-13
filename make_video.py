import os
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

if not os.path.exists("story.txt"):
    raise FileNotFoundError("story.txt missing")

if not os.path.exists("voice.mp3"):
    raise FileNotFoundError("voice.mp3 missing")

with open("story.txt", "r", encoding="utf-8") as f:
    story = f.read()

# Audio duration
result = subprocess.check_output([
    "ffprobe", "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    "voice.mp3"
])

duration = float(result.decode().strip())

os.makedirs("scenes", exist_ok=True)

font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
font = ImageFont.truetype(font_path, 45)

paragraphs = [
    p.strip() for p in story.split("\n")
    if len(p.strip()) > 20
]

if not paragraphs:
    paragraphs = [story]

scene_count = min(10, len(paragraphs))
scenes = paragraphs[:scene_count]

for i, paragraph in enumerate(scenes):
    img = Image.new("RGB", (1280, 720), (25, 25, 35))
    draw = ImageDraw.Draw(img)

    draw.text(
        (640, 100),
        "HINDI MORAL STORY",
        fill="gold",
        font=ImageFont.truetype(font_path, 55),
        anchor="mm"
    )

    wrapped = textwrap.fill(paragraph, width=30)

    draw.multiline_text(
        (640, 360),
        wrapped,
        fill="white",
        font=font,
        anchor="mm",
        align="center",
        spacing=20
    )

    img.save(f"scenes/scene_{i}.png")

# Create video with FFmpeg
scene_duration = duration / scene_count

with open("scenes.txt", "w") as f:
    for i in range(scene_count):
        f.write(f"file 'scenes/scene_{i}.png'\n")
        f.write(f"duration {scene_duration}\n")

    f.write(f"file 'scenes/scene_{scene_count-1}.png'\n")

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", "scenes.txt",
    "-i", "voice.mp3",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-shortest",
    "-movflags", "+faststart",
    "final_video.mp4"
], check=True)

print("SUCCESS: final_video.mp4 created!")
