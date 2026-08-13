import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")


if api_key:
    print("GEMINI_API_KEY loaded successfully.")
    print("API key is hidden for security.")
else:
    print("ERROR: GEMINI_API_KEY was not found.")