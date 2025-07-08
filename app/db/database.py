import aiomysql
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        for i in range(10):  # 10 спроб
            try:
                self.pool = await aiomysql.create_pool(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASS,
                    db=DB_NAME,
                    autocommit=True
                )
                print("✅ Connected to DB!")
                return
            except Exception as e:
                print(f"🔁 [{i+1}/10] Connection failed: {e}")
                await asyncio.sleep(3)
        raise Exception("❌ Could not connect to DB after 10 attempts.")

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


    async def execute(self, query, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                return cur
