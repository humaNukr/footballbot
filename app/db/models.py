from app.db.database import Database
import pytz
from datetime import datetime

async def add_user(db: Database, telegram_id, username=None, first_name=None, last_name=None):
    query = """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET username = $4, first_name = $5
            """
    await db.execute(query, (
        telegram_id, username, first_name,
        username, first_name
    ))

async def get_all_users(db: Database):
    """Отримати список всіх користувачів"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, created_at
            FROM users 
            ORDER BY created_at DESC 
            """
    return await db.fetchall(query)

async def get_users_count(db: Database):
    """Отримати загальну кількість користувачів"""
    query = "SELECT COUNT(*) FROM users"
    result = await db.fetchone(query)
    return result[0] if result else 0

async def get_user_by_id(db: Database, telegram_id):
    """Знайти користувача за telegram_id"""
    try:
        query = "SELECT telegram_id, username, first_name, is_admin FROM users WHERE telegram_id = $1"
        user = await db.fetchone(query, (telegram_id,))
        print(f"[DEBUG] Found user: {user}")
        return user
    except Exception as e:
        print(f"[ERROR] Error in get_user_by_id: {e}")
        raise

async def search_users(db: Database, search_term):
    """Пошук користувачів за ім'ям або username"""
    query = """
            SELECT telegram_id, username, first_name, is_admin, created_at
            FROM users
            WHERE first_name ILIKE $1 OR username ILIKE $2
                LIMIT 20
            """
    try:
        search_pattern = f"%{search_term}%"
        users = await db.fetchall(query, (search_pattern, search_pattern))
        print(f"[DEBUG] Found users: {users}")
        return users
    except Exception as e:
        print(f"[ERROR] Error in search_users: {e}")
        raise

async def make_admin(db: Database, telegram_id):
    """Зробити користувача адміном"""
    query = "UPDATE users SET is_admin = TRUE WHERE telegram_id = $1"
    await db.execute(query, (telegram_id,))

async def remove_admin(db: Database, telegram_id):
    """Прибрати права адміна"""
    query = "UPDATE users SET is_admin = FALSE WHERE telegram_id = $1"
    await db.execute(query, (telegram_id,))

async def get_admins(db: Database):
    """Отримати список всіх адмінів"""
    query = "SELECT telegram_id, username, first_name FROM users WHERE is_admin = TRUE"
    return await db.fetchall(query)

async def save_feedback(db: Database, user_id: int, feedback_text: str):
    # Отримуємо дані користувача
    query_get_user = """
                     SELECT first_name, username FROM users WHERE telegram_id = $1
                     """
    user = await db.fetchone(query_get_user, (user_id,))
    if not user:
        raise ValueError("Користувача не знайдено в базі.")
    
    first_name, username = user

    # Зберігаємо відгук
    query_insert_feedback = """
                            INSERT INTO feedback (telegram_id, first_name, username, feedback_text)
                            VALUES ($1, $2, $3, $4)
                            """
    await db.execute(query_insert_feedback, (user_id, first_name, username, feedback_text))
    
    return first_name, username

async def log_broadcast(db: Database, message_text: str):
    # Створюємо таблицю broadcasts якщо не існує
    create_table_query = """
            CREATE TABLE IF NOT EXISTS broadcasts (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                sent_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
    await db.execute(create_table_query)
    
    query = """
            INSERT INTO broadcasts (message)
            VALUES ($1)
            """
    await db.execute(query, (message_text,))

async def get_stats(db: Database):
    # Загальна кількість користувачів
    total_users_result = await db.fetchone("SELECT COUNT(*) FROM users")
    total_users = total_users_result[0] if total_users_result else 0

    # Кількість адмінів
    total_admins_result = await db.fetchone("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
    total_admins = total_admins_result[0] if total_admins_result else 0

    # Нові користувачі сьогодні
    today_users_result = await db.fetchone("""
                          SELECT COUNT(*) FROM users
                          WHERE DATE(created_at) = CURRENT_DATE
                          """)
    today_users = today_users_result[0] if today_users_result else 0

    # Кількість відгуків
    total_feedbacks_result = await db.fetchone("SELECT COUNT(*) FROM feedback")
    total_feedbacks = total_feedbacks_result[0] if total_feedbacks_result else 0

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "today_users": today_users,
        "feedbacks": total_feedbacks
    }

async def add_schedule(db: Database, telegram_id: int, date_: str, time_: str, message_: str):
    # Отримуємо дані організатора
    query_get_user = """
                     SELECT first_name, username FROM users WHERE telegram_id = $1
                     """
    user = await db.fetchone(query_get_user, (telegram_id,))
    if not user:
        raise ValueError("Користувача не знайдено в базі.")
    
    first_name, username = user
    
    # Конвертуємо рядок дати в об'єкт дати
    date_obj = datetime.strptime(date_, "%Y-%m-%d").date()
    
    query = """
            INSERT INTO schedule (first_name, date, time, message)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """
    result = await db.fetchone(query, (first_name, date_obj, time_, message_))
    return result[0] if result else None  # Повертаємо ID нового матчу

