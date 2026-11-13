import subprocess
import re
from pathlib import Path
from PIL import Image, ImageOps

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
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio)
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return float(result.stdout.strip())


def timestamp(seconds):
    milliseconds = int(seconds * 1000)

    hours = milliseconds // 3600000
    minutes = (milliseconds % 3600000) // 60000
    secs = (milliseconds % 60000) // 1000
    ms = milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def main():

    print("Starting video creation...")

    if not STORY_FILE.exists():
        raise FileNotFoundError("story.txt missing!")

    if not VOICE_FILE.exists():
        raise FileNotFoundError("voice.mp3 missing!")

    if not IMAGE_DIR.exists():
        raise FileNotFoundError("scenes folder missing!")

    story = STORY_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not story:
        raise ValueError("Story is empty!")

    images = sorted(
        IMAGE_DIR.glob("scene_*.jpg")
    )

    if not images:
        raise FileNotFoundError(
            "No cartoon images found in scenes folder!"
        )

    duration = get_duration(VOICE_FILE)

    if duration <= 0:
        raise ValueError("Invalid audio duration!")

    prepared = []

    print("Preparing cartoon images...")

    for index, image_path in enumerate(images, start=1):

        with Image.open(image_path) as original:
            image = ImageOps.fit(
                original.convert("RGB"),
                (WIDTH, HEIGHT),
                method=Image.Resampling.LANCZOS
            )

        output = IMAGE_DIR / f"prepared_{index:02}.jpg"

        image.save(output, quality=95)

        prepared.append(output)

        print(f"Image {index}/{len(images)} ready")

    print("Creating Hindi subtitles...")

    sentences = re.split(
        r'(?<=[।!?])\s+',
        story
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    subtitle_file = Path("subtitles.srt")

    subtitle_duration = duration / max(
        1,
        len(sentences)
    )

    with subtitle_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        for index, sentence in enumerate(
            sentences,
            start=1
        ):

            start = (index - 1) * subtitle_duration
            end = min(
                index * subtitle_duration,
                duration
            )

            file.write(f"{index}\n")
            file.write(
                f"{timestamp(start)} --> {timestamp(end)}\n"
            )
            file.write(sentence + "\n\n")

    print("Creating image sequence...")

    scene_duration = duration / len(prepared)

    concat_file = Path("scenes_list.txt")

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        for image in prepared:

            file.write(
                f"file '{image.resolve()}'\n"
            )

            file.write(
                f"duration {scene_duration:.4f}\n"
            )

        file.write(
            f"file '{prepared[-1].resolve()}'\n"
        )

    print("Combining images, voice and subtitles...")

    subtitle_filter = (
        "subtitles=subtitles.srt:"
        "force_style='FontName=Noto Sans Devanagari,"
        "FontSize=24,Alignment=2,"
        "Outline=2,Shadow=1'"
    )

    run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-i", str(VOICE_FILE),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf",
        f"fps={FPS},scale={WIDTH}:{HEIGHT},"
        f"{subtitle_filter},format=yuv420p",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUTPUT_FILE)
    ])

    print("==============================")
    print("VIDEO CREATED SUCCESSFULLY!")
    print("Cartoon images:", len(prepared))
    print("Hindi voice: READY")
    print("Hindi subtitles: READY")
    print("Video:", OUTPUT_FILE)
    print("==============================")


if __name__ == "__main__":
    main()
