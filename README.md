# 🤖 Discord Bots — ระบบ 5 Bot

## โครงสร้าง

```
discord-bots/
├── .env                        ← sensitive data (token, api key)
├── .env.example                ← ตัวอย่าง .env
├── requirements.txt
├── run_all.py                  ← รันทุก bot พร้อมกัน
├── shared/
│   ├── config.py               ← โหลด .env
│   ├── database.py             ← SQLite กลาง
│   └── voice_utils.py          ← join/leave/TTS
├── bots/
│   ├── secretary/
│   │   ├── main.py
│   │   ├── config.py           ← ตั้งค่าเลขา
│   │   └── cogs/
│   │       ├── roles.py        ← ticket, clearticket, show, count, role, add/remove_role
│   │       ├── points.py       ← voice tracking + แต้ม
│   │       ├── reward.py       ← !reward, !redeem, !points
│   │       └── ai.py           ← mention bot → Groq ตอบ
│   ├── guard/
│   │   ├── main.py
│   │   ├── config.py           ← ตั้งค่ายาม
│   │   └── cogs/
│   │       ├── patrol.py       ← ลาดตระเวนวนไปเรื่อยๆ
│   │       └── kick.py         ← /เตะ @member + TTS
│   └── employees/
│       ├── base.py             ← BaseEmployee class
│       ├── config.py           ← ตั้งค่าพนักงาน
│       ├── emp1.py
│       ├── emp2.py
│       └── emp3.py
└── data/
    └── bots.db                 ← สร้างอัตโนมัติ
```

---

## ติดตั้ง

### 1. ติดตั้ง dependencies
```bash
pip install -r requirements.txt
```

### 2. ติดตั้ง ffmpeg
**Windows:** https://ffmpeg.org/download.html → เพิ่ม PATH
**Mac:** `brew install ffmpeg`
**Linux:** `sudo apt install ffmpeg`

### 3. ตั้งค่า .env
```bash
cp .env.example .env
# แก้ไขใส่ token จริง
```

### 4. สร้าง Bot บน Discord Developer Portal
1. ไปที่ https://discord.com/developers/applications
2. สร้าง Application 5 ตัว
3. Bot → Reset Token → copy ใส่ .env
4. เปิด Privileged Intents: **Server Members** + **Message Content**
5. Permissions ที่ต้องการ:
   - เลขา: `Manage Roles`
   - ยาม: `Move Members`, `Connect`, `Speak`
   - พนักงาน: `Connect`

### 5. ตั้งค่า config.py แต่ละ bot
- `bots/secretary/config.py` — AFK channel, แต้ม, reward roles
- `bots/guard/config.py` — ห้องหลัก, ห้องเตะ, ตาราง, ข้อความ TTS
- `bots/employees/config.py` — เวลาทำงาน, ห้องที่อนุญาต

### 6. รัน
```bash
python run_all.py
```

---

## คำสั่งทั้งหมด

### 📋 เลขา

| คำสั่ง | หน้าที่ | สิทธิ์ |
|--------|---------|--------|
| `/ticket @member` | เพิ่ม ticket role ตามลำดับ | Admin |
| `/clearticket` | ลบ ticket role ทุกคน | Admin |
| `!show role` | แสดง role ทั้งหมด + จำนวนคน | Admin |
| `!count <role>` | นับคนที่มี role | Admin |
| `!role <role>` | แสดงรายชื่อคนที่มี role | Admin |
| `!add_role @member @role` | เพิ่ม role | Admin |
| `!remove_role @member @role` | ถอด role | Admin |
| `!reward` | ดูรายการ reward | ทุกคน |
| `!redeem <ลำดับ>` | แลกแต้มเป็น role | ทุกคน |
| `!points` | ดูแต้มของตัวเอง | ทุกคน |
| `@บอท <ข้อความ>` | คุยกับ AI | ทุกคน |

### 🛡️ ยาม

| คำสั่ง | หน้าที่ | สิทธิ์ |
|--------|---------|--------|
| `/เตะ @member` | เตะ member พร้อม TTS | Admin |
| *(อัตโนมัติ)* | ลาดตระเวนวนไปเรื่อยๆ 24 ชม. | — |

### 👷 พนักงาน 1-3
*(ทำงานอัตโนมัติทั้งหมด — สุ่มห้อง voice ในเวลาทำงาน)*

---

## ระบบแต้ม

- เข้า voice channel → เริ่มนับเวลา
- ออก voice channel → คิดแต้ม (1 นาที = POINTS_PER_MINUTE แต้ม)
- ห้อง AFK ไม่นับ
- ใช้ `!points` ดูแต้ม
- ใช้ `!reward` ดูของที่แลกได้
- ใช้ `!redeem <ลำดับ>` แลกแต้มเป็น Role
