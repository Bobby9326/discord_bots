"""bots/employees/emp2.py — พนักงาน 2"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from base import BaseEmployee


class Employee2(BaseEmployee):
    bot_name  = "พนักงาน2"
    token_key = "EMP2"


if __name__ == "__main__":
    asyncio.run(Employee2().start_bot())
