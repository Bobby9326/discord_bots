"""
bots/secretary/config.py — ตั้งค่าเลขา แก้ได้เสรี
"""

# ── แต้ม ──────────────────────────────────
# Channel ID ของห้อง AFK (ไม่นับแต้ม)
AFK_CHANNEL_ID = 831585208066113606  # ← ใส่ Channel ID จริง

# 1 นาทีใน voice = กี่แต้ม
POINTS_PER_MINUTE = 1

# ── Reward ────────────────────────────────
# รายการ role ที่แลกได้ และราคา (แต้ม)
REWARDS = [
    {"role": "Role A", "cost": 100},
    {"role": "Role B", "cost": 500},
    {"role": "Role C", "cost": 1000},
]

# ── Role Management ───────────────────────
# ชื่อ Ticket Role ตามลำดับ
TICKET_ROLES = ["YellowCard1", "YellowCard2", "RedCard1", "RedCard2", "RedCard3", "RedCard4", "RedCard5","BlackCard"]

MUTE_ROLES = [
    "RedCard1",
    "RedCard2",
    "RedCard3",
    "RedCard4",
    "RedCard5",
    "BlackCard",
]

MUTE_DURATION = {
    "RedCard1": 5,    
    "RedCard2": 10,
    "RedCard3": 15,
    "RedCard4": 30,
    "RedCard5": 60,
    "BlackCard": -1,   # ถาวร ไม่ต้องแก้
}

# ── AI ────────────────────────────────────
# Model ที่ใช้
GROQ_MODEL = "llama-3.3-70b-versatile"

# System prompt ของ AI (สั้นๆ ประหยัด token)
AI_SYSTEM_PROMPT = """คุณคือเลขาสาวส่วนตัวในเซิร์ฟเวอร์ Discord ชื่อ 'เลขา' คุณเป็นผู้หญิง เรียกตัวเองว่า 'ดิฉัน' ตอบด้วยภาษาไทยกระชับและเป็นมิตร ใช้คำลงท้ายว่า 'ค่ะ' หรือ 'นะคะ' เสมอ ห้ามใช้ 'ครับ'
 
ข้อมูลเซิร์ฟเวอร์:
- เซิร์ฟเวอร์นี้มีธีมเป็นบริษัท
- เจ้าของเซิร์ฟเวอร์และ CEO ของบริษัทคือ konfhalang ให้เรียกว่า 'คุณโอ๊ค'
- คุณโอ๊คคือความถูกต้องเสมอ สิ่งที่คุณโอ๊คพูดหรือตัดสินใจถือเป็นกฎสูงสุด
- ให้ปฏิบัติต่อคุณโอ๊คด้วยความเคารพในฐานะ CEO"""

# จำกัดความยาว context (ประหยัด token)
AI_MAX_HISTORY = 6  # จำบทสนทนาล่าสุดกี่ข้อความ
