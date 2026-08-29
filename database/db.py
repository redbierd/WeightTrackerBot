import os
import aiosqlite
from datetime import datetime
from typing import Optional, List

if os.path.exists("/app/data"):
    DB_PATH = "/app/data/data.db"
else:
    DB_PATH = "data.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                current_weight REAL NOT NULL,
                goal_weight REAL NOT NULL,
                start_weight REAL NOT NULL,
                lifestyle TEXT NOT NULL DEFAULT 'moderate',
                timeline_months INTEGER NOT NULL DEFAULT 3,
                daily_calories INTEGER NOT NULL DEFAULT 2000,
                registered_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                hour INTEGER NOT NULL DEFAULT 9,
                enabled INTEGER NOT NULL DEFAULT 0,
                q1 INTEGER NOT NULL DEFAULT 1,
                q2 INTEGER NOT NULL DEFAULT 1,
                q3 INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (user_id, type),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        await db.commit()


async def add_user(user_id: int, name: str, age: int, current_weight: float,
                   goal_weight: float, lifestyle: str, timeline_months: int, daily_calories: int):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO users
            (user_id, name, age, current_weight, goal_weight, start_weight,
             lifestyle, timeline_months, daily_calories, registered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, age, current_weight, goal_weight, current_weight,
             lifestyle, timeline_months, daily_calories, now)
        )
        await db.execute(
            "INSERT INTO weight_history (user_id, weight, date) VALUES (?, ?, ?)",
            (user_id, current_weight, now)
        )
        await db.commit()


async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_weight(user_id: int, weight: float):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET current_weight = ? WHERE user_id = ?", (weight, user_id))
        await db.execute(
            "INSERT INTO weight_history (user_id, weight, date) VALUES (?, ?, ?)",
            (user_id, weight, now)
        )
        await db.commit()


async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM weight_history WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()


async def user_exists(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None


async def init_notification(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO notifications (user_id, type, hour, enabled, q1, q2, q3)
            VALUES (?, 'morning', 8, 0, 1, 1, 1)
        """, (user_id,))
        await db.execute("""
            INSERT OR IGNORE INTO notifications (user_id, type, hour, enabled, q1, q2, q3)
            VALUES (?, 'evening', 21, 0, 1, 1, 1)
        """, (user_id,))
        await db.commit()


async def get_notification(user_id: int, ntype: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM notifications WHERE user_id = ? AND type = ?",
            (user_id, ntype)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_notification(user_id: int, ntype: str, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(
                f"UPDATE notifications SET {key} = ? WHERE user_id = ? AND type = ?",
                (value, user_id, ntype)
            )
        await db.commit()


async def get_active_notifications(hour: int, minute: int) -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM notifications WHERE enabled = 1 AND hour = ?",
            (hour,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
