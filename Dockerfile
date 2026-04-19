FROM python:3.13-slim

# ติดตั้ง ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# ตั้ง working directory
WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy โค้ดทั้งหมด
COPY . .

# ตั้งค่า encoding
ENV PYTHONUTF8=1

# รัน bot
CMD ["python", "run_all.py"]