# src/config_gemini.py
import os
from functools import lru_cache
from google import genai


class MissingGeminiKey(RuntimeError):
    pass


@lru_cache
def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise MissingGeminiKey(
            "GEMINI_API_KEY is not set. "
            "Create a .env file with GEMINI_API_KEY=... or export it in your shell."
        )
    return genai.Client(api_key=api_key)
