import os
import re
import time
import base64
import requests
from pathlib import Path

# Cloudflare credentials
ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
API_TOKEN = os.getenv("CF_API_TOKEN")

if not ACCOUNT_ID or not API_TOKEN:
    raise ValueError("Cloudflare API credentials missing!")

# Settings
MODEL = "@cf/black-forest-labs/flux-1-schnell"

API_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/{MODEL}"
)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

STORY_FILE = Path("story.txt")
OUTPUT_DIR = Path("scenes")

# Check story
if not STORY_FILE.exists():
    raise FileNotFoundError("story.txt file not found!")

story = STORY_FILE.read_text(encoding="utf-8").strip()

if not story:
    raise ValueError("Story is empty!")

OUTPUT_DIR.mkdir(exist_ok=True)

# Divide story into scenes
sentences = re.split(r'(?<=[.!?।])\s+', story)
sentences = [s.strip() for s in sentences if s.strip()]

if not sentences:
    raise ValueError("No story scenes found!")

scene_count = min(8, len(sentences))
scenes = []

for i in range(scene_count):
    start = i * len(sentences) // scene_count
    end = (i + 1) * len(sentences) // scene_count
    scenes.append(" ".join(sentences[start:end]))

# Cartoon style
STYLE = """
Professional 2D Indian children's moral story cartoon illustration,
beautiful expressive cartoon characters, colorful Indian village,
cinematic composition, detailed background, clean outlines,
high quality animation concept art, landscape 16:9 composition.
No text, no watermark, no letters.
"""

# Generate images
for number, scene in enumerate(scenes, start=1):

    prompt = (
        STYLE
        + " Show this story scene: "
        + scene[:700]
    )

    print(f"Generating scene {number}/{scene_count}...")

    success = False

    for attempt in range(3):

        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={
                    "prompt": prompt,
                    "steps": 4
                },
                timeout=180
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                raise RuntimeError(str(data.get("errors", data)))

            result = data.get("result", {})
            image_data = result.get("image")

            if not image_data:
                raise RuntimeError("Image data not found!")

            image_bytes = base64.b64decode(image_data)

            output_file = OUTPUT_DIR / f"scene_{number:02d}.jpg"

            output_file.write_bytes(image_bytes)

            print(f"Saved: {output_file}")

            success = True
            break

        except Exception as error:
            print(f"Attempt {attempt + 1} failed: {error}")

            if attempt < 2:
                time.sleep(10)

    if not success:
        raise RuntimeError(
            f"Could not generate scene {number}"
        )

    time.sleep(2)

print("--------------------------------")
print("ALL CARTOON SCENES GENERATED!")
print(f"Total images: {scene_count}")
print(f"Images saved in: {OUTPUT_DIR}")
print("--------------------------------")
