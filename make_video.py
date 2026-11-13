import subprocess
from pathlib import Path
from PIL import Image, ImageOps
import re

STORY_FILE = Path("story.txt")
VOICE_FILE = Path("voice.mp3")
IMAGE_DIR = Path("scenes")
OUTPUT_FILE = Path("final_video.mp4")

WIDTH = 1280
HEIGHT = 720
FPS = 25

def run(command):
subprocess.run(command, check=True)

def get_duration(audio):
result = subprocess.run(
[
"ffprobe", "-v", "error",
"-show_entries", "format=duration",
"-of", "default=noprint_wrappers=1:nokey=1",
str(audio)
],
capture_output=True,
text=True,
check=True
)
return float(result.stdout.strip())

Check files

for path in [STORY_FILE, VOICE_FILE, IMAGE_DIR]:
if not path.exists():
raise FileNotFoundError(f"Missing: {path}")

story = STORY_FILE.read_text(encoding="utf-8").strip()

if not story:
raise ValueError("Story is empty!")

images = sorted(IMAGE_DIR.glob("scene_*.jpg"))

if not images:
raise FileNotFoundError("No cartoon images found!")

duration = get_duration(VOICE_FILE)

if duration <= 0:
raise ValueError("Invalid voice duration!")

Prepare cartoon images

prepared = []

for index, image_path in enumerate(images, start=1):
image = Image.open(image_path).convert("RGB")

image = ImageOps.fit(
    image,
    (WIDTH, HEIGHT),
    method=Image.Resampling.LANCZOS
)

output = IMAGE_DIR / f"prepared_{index:02d}.jpg"
image.save(output, quality=95)
prepared.append(output)

print(f"Image prepared: {index}/{len(images)}")

Split story into subtitle lines

sentences = re.split(r'(?<=[।!?])\s+', story)
sentences = [s.strip() for s in sentences if s.strip()]

Create subtitle file

subtitle_file = Path("subtitles.srt")
subtitle_duration = duration / max(1, len(sentences))

def timestamp(seconds):
milliseconds = int(seconds * 1000)
hours = milliseconds // 3600000
minutes = (milliseconds % 3600000) // 60000
seconds_part = (milliseconds % 60000) // 1000
ms = milliseconds % 1000
return f"{hours:02}:{minutes:02}:{seconds_part:02},{ms:03}"

with subtitle_file.open("w", encoding="utf-8") as f:
for i, sentence in enumerate(sentences, start=1):
start = (i - 1) * subtitle_duration
end = min(i * subtitle_duration, duration)

    f.write(f"{i}\n")
    f.write(f"{timestamp(start)} --> {timestamp(end)}\n")
    f.write(sentence + "\n\n")

Create image sequence

scene_duration = duration / len(prepared)

concat_file = Path("scenes_list.txt")

with concat_file.open("w", encoding="utf-8") as f:
for image in prepared:
f.write(f"file '{image.resolve()}'\n")
f.write(f"duration {scene_duration:.4f}\n")

f.write(f"file '{prepared[-1].resolve()}'\n")

Generate video with subtitles and Hindi voice

subtitle_filter = (
"subtitles=subtitles.srt:"
"force_style='FontName=Noto Sans Devanagari,"
"FontSize=24,Alignment=2,"
"Outline=2,Shadow=1'"
)

run([
"ffmpeg", "-y",
"-f", "concat",
"-safe", "0",
"-i", str(concat_file),
"-i", str(VOICE_FILE),
"-map", "0:v:0",
"-map", "1:a:0",
"-vf", f"fps={FPS},scale={WIDTH}:{HEIGHT},{subtitle_filter},format=yuv420p",
"-t", str(duration),
"-c:v", "libx264",
"-preset", "veryfast",
"-crf", "23",
"-c:a", "aac",
"-b:a", "192k",
"-movflags", "+faststart",
str(OUTPUT_FILE)
])

print("================================")
print("AI CARTOON VIDEO CREATED!")
print("Hindi voice: READY")
print("Cartoon images:", len(prepared))
print("Hindi subtitles: READY")
print("Video:", OUTPUT_FILE)
print("================================")
