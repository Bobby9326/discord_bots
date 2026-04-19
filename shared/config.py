"""
shared/config.py — โหลด sensitive data จาก .env เท่านั้น
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_token(bot_name: str) -> str:
    key = f"DISCORD_TOKEN_{bot_name.upper()}"
    token = os.getenv(key)
    if not token:
        raise ValueError(f"❌ ไม่พบ {key} ใน .env")
    return token


GROQ_API_KEY:   str = os.getenv("GROQ_API_KEY", "")
SUPABASE_URL:   str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY:   str = os.getenv("SUPABASE_KEY", "")