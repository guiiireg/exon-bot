"""Database for the bot using aiosqlite

Handles asynchronous SQLite database init, table creation
and execution of queries for persistent feature like user warnings.
"""

import aiosqlite


class DatabaseManager:
    def __init__(self, db_path: str = "bot_data.db") -> None:
        self.db_path = db_path

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    async def add_warning(
        self, user_id: int, guild_id: int, moderator_id: int, reason: str
    ) -> int:
        """Insert a new warning record into the database

        Args:
            user_id: The discord ID of the warned member
            guild_id: The discord ID of the guild
            moderator_id: The discord IF of the moderator issuing the warning
            reason: Explanation text for the warning

        Returns:
            The primary key ID of the newly inserted warning
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO warnings (user_id, guild_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, guild_id, moderator_id, reason),
            )
            await db.commit()
            return cursor.lastrowid or 0

    async def get_warnings(self, user_id: int, guild_id: int) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT id, moderator_id, reason, created_at
                FROM warnings
                WHERE user_id = ? AND guild_id = ?
                ORDER BY created_at DESC
                """,
                (user_id, guild_id),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
