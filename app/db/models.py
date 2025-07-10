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

async def get_all_users(db: Database, limit=10, offset=0):
    """Отримати список всіх користувачів"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
            """
    result = await db.execute(query, (limit, offset))
    return await result.fetchall()

async def get_users_count(db: Database):
    """Отримати загальну кількість користувачів"""
    query = "SELECT COUNT(*) FROM users"
    result = await db.execute(query)
    row = await result.fetchone()
    return row[0] if row else 0

async def get_user_by_id(db: Database, telegram_id):
    """Знайти користувача за telegram_id"""
    query = "SELECT telegram_id, username, first_name, is_admin, created_at FROM users WHERE telegram_id = %s"
    result = await db.execute(query, (telegram_id,))
    return await result.fetchone()

async def search_users(db: Database, search_term):
    """Пошук користувачів за ім'ям або username"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, created_at
            FROM users 
            WHERE first_name LIKE %s OR username LIKE %s
            LIMIT 20
            """
    search_pattern = f"%{search_term}%"
    result = await db.execute(query, (search_pattern, search_pattern))
    return await result.fetchall()

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

async def get_stats(db: Database):
    """Отримати статистику боту"""
    stats = {}
    
    # Загальна кількість користувачів
    result = await db.execute("SELECT COUNT(*) FROM users")
    row = await result.fetchone()
    stats['total_users'] = row[0] if row else 0
    
    # Кількість адмінів
    result = await db.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    row = await result.fetchone()
    stats['total_admins'] = row[0] if row else 0
    
    # Користувачі за сьогодні
    result = await db.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
    row = await result.fetchone()
    stats['today_users'] = row[0] if row else 0
    
    return stats
