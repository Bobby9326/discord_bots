"""bots/employees/emp1.py — พนักงาน 1"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from base import BaseEmployee


class Employee1(BaseEmployee):
    bot_name  = "พนักงาน1"
    token_key = "EMP1"


if __name__ == "__main__":
    asyncio.run(Employee1().start_bot())
