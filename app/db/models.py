from app.db.database import Database

async def add_user(db: Database, telegram_id, username=None, first_name=None, last_name=None):
    query = """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE username=%s, first_name=%s
            """
    await db.execute(query, (
        telegram_id, username, first_name,
        username, first_name
    ))

async def get_all_users(db: Database):
    """Отримати список всіх користувачів"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, registered_at
            FROM users 
            ORDER BY registered_at DESC 
            """
    result = await db.execute(query)
    return await result.fetchall()

async def get_users_count(db: Database):
    """Отримати загальну кількість користувачів"""
    query = "SELECT COUNT(*) FROM users"
    result = await db.execute(query)
    row = await result.fetchone()
    return row[0] if row else 0

async def get_user_by_id(db: Database, telegram_id):
    """Знайти користувача за telegram_id"""
    try:
        query = "SELECT telegram_id, username, first_name, is_admin FROM users WHERE telegram_id = %s"
        result = await db.execute(query, (telegram_id,))
        user = await result.fetchone()
        print(f"[DEBUG] Found user: {user}")
        return user
    except Exception as e:
        print(f"[ERROR] Error in get_user_by_id: {e}")
        raise

async def search_users(db: Database, search_term):
    """Пошук користувачів за ім'ям або username"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, registered_at
            FROM users
            WHERE first_name LIKE %s OR username LIKE %s
                LIMIT 20
            """
    try:
        search_pattern = f"%{search_term}%"
        result = await db.execute(query, (search_pattern, search_pattern))
        users = await result.fetchall()
        print(f"[DEBUG] Found users: {users}")
        return users
    except Exception as e:
        print(f"[ERROR] Error in search_users: {e}")
        raise

async def make_admin(db: Database, telegram_id):
    """Зробити користувача адміном"""
    query = "UPDATE users SET is_admin = 1 WHERE telegram_id = %s"
    await db.execute(query, (telegram_id,))

async def remove_admin(db: Database, telegram_id):
    """Прибрати права адміна"""
    query = "UPDATE users SET is_admin = 0 WHERE telegram_id = %s"
    await db.execute(query, (telegram_id,))

async def get_admins(db: Database):
    """Отримати список всіх адмінів"""
    query = "SELECT telegram_id, username, first_name FROM users WHERE is_admin = 1"
    result = await db.execute(query)
    return await result.fetchall()

async def save_feedback(db: Database, user_id: int, feedback_text: str):
    query_get_user = """
                     SELECT first_name, username FROM users WHERE telegram_id = %s \
                     """
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query_get_user, (user_id,))
            user = await cur.fetchone()
            if not user:
                raise ValueError("Користувача не знайдено в базі.")
            first_name, username = user


    query_insert_feedback = """
                            INSERT INTO feedback (user_id, first_name, username, feedback_text, created_at)
                            VALUES (%s, %s, %s, %s, NOW()) \
                            """
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query_insert_feedback, (user_id, first_name, username, feedback_text))



async def log_broadcast(db: Database, message_text: str):
    query = """
            INSERT INTO broadcasts (message, sent_at)
            VALUES (%s, NOW()) \
            """
    await db.execute(query, (message_text,))

async def get_stats(db: Database):
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM users")
            total_users = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            total_admins = (await cur.fetchone())[0]

            await cur.execute("""
                              SELECT COUNT(*) FROM users
                              WHERE DATE(registered_at) = CURRENT_DATE()
                              """)
            today_users = (await cur.fetchone())[0]

            await cur.execute("SELECT COUNT(*) FROM feedback")
            total_feedbacks = (await cur.fetchone())[0]

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "today_users": today_users,
        "feedbacks": total_feedbacks
    }
