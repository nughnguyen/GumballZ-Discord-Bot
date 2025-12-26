import aiosqlite
import os

class CoinsDB:
    def __init__(self, db_path="db/coiz.db"):
        self.db_path = db_path

    async def initialize(self):
        if not os.path.exists("db"):
            os.makedirs("db")
        async with aiosqlite.connect(self.db_path) as db:
            # We use a new table name 'coiz_balances' to avoid conflicts with corrupted 'player_stats'
            await db.execute("""
                CREATE TABLE IF NOT EXISTS coiz_balances (
                    user_id INTEGER,
                    guild_id INTEGER,
                    total_points REAL DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await db.commit()

    async def get_player_points(self, user_id, guild_id):
        # We use guild_id=0 for global points as in the game logic
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT total_points FROM coiz_balances WHERE user_id = ? AND guild_id = 0", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return 0

    async def add_points(self, user_id, guild_id, points):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT total_points FROM coiz_balances WHERE user_id = ? AND guild_id = 0", (user_id,)) as cursor:
                row = await cursor.fetchone()
            
            if row:
                new_points = row[0] + points
                await db.execute("UPDATE coiz_balances SET total_points = ? WHERE user_id = ? AND guild_id = 0", (new_points, user_id))
            else:
                await db.execute("INSERT INTO coiz_balances (user_id, guild_id, total_points) VALUES (?, 0, ?)", (user_id, points))
            await db.commit()
