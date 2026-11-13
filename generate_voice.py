from gtts import gTTS
import os

if not os.path.exists("story.txt"):
    raise FileNotFoundError("Story file missing!")

with open("story.txt", "r", encoding="utf-8") as f:
    story = f.read()

if not story.strip():
    raise ValueError("Story is empty!")

tts = gTTS(
    text=story,
    lang="hi",
    slow=False
)

tts.save("voice.mp3")

print("Hindi voice generated successfully!")
