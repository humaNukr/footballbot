import asyncpg
import os
from dotenv import load_dotenv
import asyncio
from urllib.parse import urlparse

load_dotenv()

# Підтримка як окремих змінних, так і DATABASE_URL (для Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Парсимо DATABASE_URL для Render
    url = urlparse(DATABASE_URL)
    DB_HOST = url.hostname
    DB_PORT = url.port or 5432
    DB_USER = url.username
    DB_PASS = url.password
    DB_NAME = url.path[1:]  # Видаляємо першу косу риску
else:
    # Локальні налаштування
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "football")
    DB_PASS = os.getenv("DB_PASS", "footballpass")
    DB_NAME = os.getenv("DB_NAME", "football_db")
    DB_PORT = os.getenv("DB_PORT", "5432")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        for i in range(10):  # 10 спроб
            try:
                connection_params = {
                    "host": DB_HOST,
                    "port": int(DB_PORT),
                    "user": DB_USER,
                    "password": DB_PASS,
                    "database": DB_NAME,
                    "min_size": 1,
                    "max_size": 10,
                    "command_timeout": 60
                }
                
                # Для production (Render) додаємо SSL
                if DATABASE_URL or os.getenv("RENDER"):
                    connection_params["ssl"] = "require"
                
                self.pool = await asyncpg.create_pool(**connection_params)
                print("✅ Connected to PostgreSQL DB!")
                
                # Створюємо основні таблиці
                await self._create_tables()
                return
            except Exception as e:
                print(f"🔁 [{i+1}/10] Connection failed: {e}")
                await asyncio.sleep(3)
        raise Exception("❌ Could not connect to DB after 10 attempts.")

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def _create_tables(self):
        """Створює всі необхідні таблиці"""
        async with self.pool.acquire() as conn:
            # Таблиця користувачів
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблиця розкладу матчів
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    message TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблиця реєстрацій на матчі
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id SERIAL PRIMARY KEY,
                    match_id INTEGER REFERENCES schedule(id) ON DELETE CASCADE,
                    telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
                    first_name VARCHAR(255),
                    username VARCHAR(255),
                    registered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    message TEXT,
                    UNIQUE(match_id, telegram_id)
                )
            """)
            
            # Таблиця відгуків
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
                    first_name VARCHAR(255),
                    username VARCHAR(255),
                    feedback_text TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)
            

            
            print("✅ Database tables created/updated")

    async def execute(self, query, params=None):
        async with self.pool.acquire() as conn:
            if params:
                return await conn.execute(query, *params)
            else:
                return await conn.execute(query)

    async def fetchone(self, query, params=None):
        async with self.pool.acquire() as conn:
            if params:
                return await conn.fetchrow(query, *params)
            else:
                return await conn.fetchrow(query)

    async def fetchall(self, query, params=None):
        async with self.pool.acquire() as conn:
            if params:
                return await conn.fetch(query, *params)
            else:
                return await conn.fetch(query)