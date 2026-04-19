"""
run_all.py — รัน Bot ทั้ง 5 ตัวพร้อมกัน (แยก process)
"""
import subprocess
import sys
import os
import signal
import time
import threading

BASE = os.path.dirname(os.path.abspath(__file__))

BOTS = [
    ("📋 เลขา",     os.path.join(BASE, "bots", "secretary", "main.py")),
    ("🛡️ ยาม",      os.path.join(BASE, "bots", "guard",     "main.py")),
    ("👷 พนักงาน1", os.path.join(BASE, "bots", "employees", "emp1.py")),
    ("👷 พนักงาน2", os.path.join(BASE, "bots", "employees", "emp2.py")),
    ("👷 พนักงาน3", os.path.join(BASE, "bots", "employees", "emp3.py")),
]

processes: list[tuple[str, str, subprocess.Popen]] = []


def make_env(path: str) -> dict:
    env = os.environ.copy()
    bot_dir = os.path.dirname(path)
    paths = [BASE, bot_dir]
    existing = env.get("PYTHONPATH", "")
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    env["PYTHONUTF8"] = "1"  # บังคับ UTF-8 บน Windows
    return env


def stream_output(name: str, proc: subprocess.Popen):
    """thread สำหรับอ่าน output ของแต่ละ bot"""
    for line in iter(proc.stdout.readline, ""):
        print(f"[{name}] {line}", end="", flush=True)


def start_bot(name: str, path: str) -> subprocess.Popen:
    p = subprocess.Popen(
        [sys.executable, "-u", path],
        env=make_env(path),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    t = threading.Thread(target=stream_output, args=(name, p), daemon=True)
    t.start()
    return p


def start_all():
    print(f"\n{'='*45}")
    print("  Discord Bots — กำลังเริ่มทุกตัว")
    print(f"{'='*45}")
    for name, path in BOTS:
        p = start_bot(name, path)
        processes.append((name, path, p))
        print(f"  ▶  {name} (PID {p.pid})")
    print(f"{'='*45}")
    print("  กด Ctrl+C เพื่อหยุดทั้งหมด")
    print(f"{'='*45}\n")


def stop_all():
    print("\n🛑 กำลังหยุด bot ทั้งหมด...")
    for _, _, p in processes:
        p.terminate()
    for _, _, p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    print("✅ หยุดทุกตัวแล้ว")


def monitor():
    while True:
        for i, (name, path, p) in enumerate(processes):
            if p.poll() is not None:
                print(f"\n⚠️  {name} หยุดทำงาน (exit {p.returncode}) — กำลัง restart...\n")
                new_p = start_bot(name, path)
                processes[i] = (name, path, new_p)
                print(f"  ▶  restart {name} (PID {new_p.pid})")
        time.sleep(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT,  lambda s, f: (stop_all(), exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (stop_all(), exit(0)))
    start_all()
    try:
        monitor()
    except KeyboardInterrupt:
        stop_all()