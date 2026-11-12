import os
import requests
from datetime import datetime

API_KEY = os.environ["GEMINI_API_KEY"]

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.5-flash-lite:generateContent"
)

prompt = """
Ek bilkul nayi Hindi moral story likho.
Story 1200-1500 words ki ho.
Bachchon aur family ke liye suitable ho.
Interesting characters aur dialogues hon.
Ending mein ek powerful moral lesson ho.
Story original honi chahiye.
Sirf Hindi mein likho.
"""

response = requests.post(
    import time
     url,
        headers={
            "x-goog-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 8192
            }
        },
        timeout=180
    )

    if response.status_code in [429, 500, 502, 503, 504]:
        print(f"Retry {attempt + 1}/5")
        time.sleep(2 ** (attempt + 1))
        continue
        
response.raise_for_status()
    break
else:
    raise Exception("Gemini service unavailable after 5 attempts")

story = response.json()["candidates"][0]["content"]["parts"][0]["text"]

with open("story.txt", "w", encoding="utf-8") as f:
    f.write(story)

print("Hindi moral story generated successfully!")
