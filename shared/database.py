"""
shared/database.py — Supabase client กลาง

ตาราง SQL ที่ต้องสร้างใน Supabase Dashboard → SQL Editor:

    CREATE TABLE points (
        user_id TEXT PRIMARY KEY,
        total   INTEGER DEFAULT 0
    );

    CREATE TABLE voice_sessions (
        user_id   TEXT PRIMARY KEY,
        joined_at TEXT NOT NULL
    );

    CREATE TABLE reward_logs (
        id          SERIAL PRIMARY KEY,
        user_id     TEXT NOT NULL,
        role_name   TEXT NOT NULL,
        cost        INTEGER NOT NULL,
        redeemed_at TEXT NOT NULL
    );
"""
from supabase import create_client, Client
from shared.config import SUPABASE_URL, SUPABASE_KEY

_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY ใน .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ── Points ────────────────────────────────

def get_points(user_id: str) -> int:
    res = get_db().table("points").select("total").eq("user_id", user_id).execute()
    return res.data[0]["total"] if res.data else 0


def add_points(user_id: str, amount: int):
    current = get_points(user_id)
    new_total = max(0, current + amount)
    get_db().table("points").upsert({
        "user_id": user_id,
        "total": new_total
    }).execute()


# ── Voice Sessions ─────────────────────────

def start_session(user_id: str, joined_at: str):
    get_db().table("voice_sessions").upsert({
        "user_id": user_id,
        "joined_at": joined_at
    }).execute()


def get_session(user_id: str) -> str | None:
    res = get_db().table("voice_sessions").select("joined_at").eq("user_id", user_id).execute()
    return res.data[0]["joined_at"] if res.data else None


def end_session(user_id: str):
    get_db().table("voice_sessions").delete().eq("user_id", user_id).execute()


# ── Reward Logs ───────────────────────────

def log_reward(user_id: str, role_name: str, cost: int, redeemed_at: str):
    get_db().table("reward_logs").insert({
        "user_id": user_id,
        "role_name": role_name,
        "cost": cost,
        "redeemed_at": redeemed_at
    }).execute()