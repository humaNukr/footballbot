from app.db.database import Database

async def add_user(db: Database, telegram_id, username=None, first_name=None, last_name=None):
    query = """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE username=%s, first_name=%s, last_name=%s
            """
    await db.execute(query, (
        telegram_id, username, first_name, last_name,
        username, first_name, last_name
    ))
