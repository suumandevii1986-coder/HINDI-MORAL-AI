from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import re

STORY_FILE = Path("story.txt")
IMAGE_DIR = Path("scenes")
OUTPUT_FILE = Path("thumbnail.jpg")

WIDTH = 1280
HEIGHT = 720

if not STORY_FILE.exists():
raise FileNotFoundError("story.txt missing!")

story = STORY_FILE.read_text(encoding="utf-8").strip()

if not story:
raise ValueError("Story is empty!")

images = sorted(IMAGE_DIR.glob("scene_*.jpg"))

if not images:
raise FileNotFoundError("Cartoon images not found!")

First cartoon scene as thumbnail background

image = Image.open(images[0]).convert("RGB")
image = image.resize((WIDTH, HEIGHT))
image = ImageEnhance.Contrast(image).enhance(1.2)
image = ImageEnhance.Color(image).enhance(1.2)

Dark overlay for readable title

overlay = Image.new("RGBA", image.size, (0, 0, 0, 95))
image = Image.alpha_composite(image.convert("RGBA"), overlay)

draw = ImageDraw.Draw(image)

Extract title from story

sentences = re.split(r'(?<=[।!?])\s+', story)
title = sentences[0].strip() if sentences else story

words = title.split()
if len(words) > 9:
title = " ".join(words[:9]) + "..."

Hindi font

font_paths = [
"/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
"/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
]

font = None

for path in font_paths:
if Path(path).exists():
font = ImageFont.truetype(path, 76)
break

if font is None:
raise FileNotFoundError("Hindi font not found!")

Wrap title into lines

lines = []
current_line = ""

for word in title.split():
test = (current_line + " " + word).strip()

if draw.textbbox((0, 0), test, font=font)[2] < 1120:
    current_line = test
else:
    if current_line:
        lines.append(current_line)
    current_line = word

if current_line:
lines.append(current_line)

lines = lines[:3]

Center title

line_heights = [
draw.textbbox((0, 0), line, font=font)[3] -
draw.textbbox((0, 0), line, font=font)[1]
for line in lines
]

total_height = sum(line_heights) + (len(lines) - 1) * 25
y = (HEIGHT - total_height) // 2

for line, line_height in zip(lines, line_heights):
bbox = draw.textbbox((0, 0), line, font=font, stroke_width=3)
text_width = bbox[2] - bbox[0]
x = (WIDTH - text_width) // 2

draw.text(
    (x, y),
    line,
    font=font,
    fill=(255, 255, 255),
    stroke_width=5,
    stroke_fill=(0, 0, 0)
)

y += line_height + 25

Small channel label

small_font = ImageFont.truetype(font_paths[0], 32)

draw.text(
(35, 35),
"HINDI MORAL STORY",
font=small_font,
fill=(255, 220, 0),
stroke_width=2,
stroke_fill=(0, 0, 0)
)

image.convert("RGB").save(
OUTPUT_FILE,
quality=95
)

print("YouTube thumbnail created successfully!")
print("File:", OUTPUT_FILE)
