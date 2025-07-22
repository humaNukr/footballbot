import aiomysql
import os
from dotenv import load_dotenv
import asyncio
from urllib.parse import urlparse

load_dotenv()

# Парсимо DATABASE_URL або використовуємо окремі змінні
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname
    DB_USER = parsed.username  
    DB_PASS = parsed.password
    DB_NAME = parsed.path[1:]  # без першого слеша
    DB_PORT = parsed.port or 3306
    print(f"✅ Використовую DATABASE_URL для підключення до MySQL")
    print(f"🔗 Host: {DB_HOST}:{DB_PORT}")
    print(f"🗄️  Database: {DB_NAME}")
else:
    # Fallback на окремі змінні
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER") 
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    print(f"✅ Використовую окремі змінні для підключення до MySQL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        print(f"🚀 Спроба підключення до MySQL...")
        print(f"📡 Хост: {DB_HOST}:{DB_PORT}")
        print(f"👤 Користувач: {DB_USER}")
        print(f"🗄️  База даних: {DB_NAME}")
        
        for i in range(10):  # 10 спроб
            try:
                self.pool = await aiomysql.create_pool(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASS,
                    db=DB_NAME,
                    autocommit=True,
                    charset='utf8mb4',
                    init_command="SET time_zone = 'Europe/Kiev'"  # Київський час з автоматичним переходом на літній час
                )
                print("✅ Успішно підключено до MySQL!")
                return
            except Exception as e:
                print(f"🔁 [{i+1}/10] Помилка підключення: {e}")
                await asyncio.sleep(3)
        raise Exception("❌ Не вдалося підключитися до MySQL після 10 спроб.")

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


    async def execute(self, query, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                return cur

    async def fetchall(self, query, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                result = await cur.fetchall()
                return result

    async def fetchone(self, query, params=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                result = await cur.fetchone()
                return result