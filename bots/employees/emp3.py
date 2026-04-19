"""bots/employees/emp3.py — พนักงาน 3"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from base import BaseEmployee


class Employee3(BaseEmployee):
    bot_name  = "พนักงาน3"
    token_key = "EMP3"


if __name__ == "__main__":
    asyncio.run(Employee3().start_bot())
