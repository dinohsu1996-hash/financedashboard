# backend/app/services/config_gemini.py
import os
from functools import lru_cache
from google import genai
from dotenv import load_dotenv

load_dotenv()

class MissingGeminiKey(RuntimeError):
    pass

@lru_cache
def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    # For now, if not found in env, check if it was passed in secrets but here we are in backend mode
    # Assuming environment variables are set
    if not api_key:
         print("Warning: GEMINI_API_KEY not found in environment variables.")
         return None

    return genai.Client(api_key=api_key)
