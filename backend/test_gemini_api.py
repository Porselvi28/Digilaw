import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD API KEY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )


# =========================================================
# CONNECT TO GEMINI
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# SEND TEST REQUEST
# =========================================================

print("\nConnecting to Gemini...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello to DigiLaw in one short sentence."
)


# =========================================================
# DISPLAY RESPONSE
# =========================================================

print("\nGemini response:")
print(response.text)

print("\nGemini API connection successful! ✅")