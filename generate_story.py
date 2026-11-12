import os
import time
import requests
from datetime import datetime

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY secret missing!")

MODEL = "gemini-3.5-flash-lite"

URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL}:generateContent"
)

prompt = """
Ek original Hindi moral story likho.

Requirements:
- Story 1200-1500 words ki ho.
- Language simple Hindi ho.
- Interesting characters hon.
- Powerful opening hook ho.
- Natural dialogues hon.
- Family friendly story ho.
- Ending emotional aur inspiring ho.
- Last mein ek powerful moral lesson ho.
- Har baar nayi story honi chahiye.
- Purani story repeat mat karna.
"""

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.9,
        "maxOutputTokens": 8192
    }
}

response = None

for attempt in range(5):

    print(f"Generating story... Attempt {attempt + 1}")

    try:
        response = requests.post(
            URL,
            headers={
                "x-goog-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=180
        )

        if response.status_code == 200:
            break

        if response.status_code in [429, 500, 502, 503, 504]:
            print("Temporary API error:", response.text[:1000])
            time.sleep(2 ** (attempt + 1))
            continue

        raise Exception(
            f"Gemini API Error {response.status_code}: "
            f"{response.text[:2000]}"
        )

    except requests.RequestException as error:
        print("Connection error:", error)
        time.sleep(2 ** (attempt + 1))

else:
    raise Exception(
        "Gemini failed after 5 attempts. "
        "Check API availability and quota."
    )

data = response.json()

try:
    story = data["candidates"][0]["content"]["parts"][0]["text"]
except (KeyError, IndexError, TypeError):
    raise Exception(f"Unexpected Gemini response: {data}")

if not story.strip():
    raise Exception("Generated story is empty!")

filename = "story.txt"

with open(filename, "w", encoding="utf-8") as file:
    file.write(story)

print("SUCCESS! Hindi moral story generated.")
print("Characters:", len(story))
print("Saved as:", filename)
