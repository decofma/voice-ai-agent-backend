# backend/app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    RETELL_API_KEY: str = os.getenv("RETELL_API_KEY", "dummy_retell_key")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "dummy_gemini_key")
    RETELL_NUMBER: str = os.getenv("RETELL_NUMBER", "+1234567890")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

settings = Settings()

# NOT IN USE, BUT COULD BE USEFUL IN FUTURE, IT'S BETTER TO USE ENV VARIABLES