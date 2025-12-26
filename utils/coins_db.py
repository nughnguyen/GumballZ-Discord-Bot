import aiosqlite
import os
import json

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
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fishing_data (
                    user_id INTEGER PRIMARY KEY,
                    inventory TEXT DEFAULT '{}',
                    stats TEXT DEFAULT '{}',
                    rod_type TEXT DEFAULT 'Plastic Rod'
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

    async def get_fishing_data(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT inventory, stats, rod_type FROM fishing_data WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    try:
                        return {
                            "inventory": json.loads(row[0]),
                            "stats": json.loads(row[1]),
                            "rod_type": row[2]
                        }
                    except:
                        return {"inventory": {}, "stats": {}, "rod_type": "Plastic Rod"}
                return {"inventory": {}, "stats": {}, "rod_type": "Plastic Rod"}

    async def update_fishing_data(self, user_id, inventory=None, stats=None, rod_type=None):
        current = await self.get_fishing_data(user_id)
        
        new_inv = inventory if inventory is not None else current["inventory"]
        new_stats = stats if stats is not None else current["stats"]
        new_rod = rod_type if rod_type is not None else current["rod_type"]
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO fishing_data (user_id, inventory, stats, rod_type)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    inventory=excluded.inventory,
                    stats=excluded.stats,
                    rod_type=excluded.rod_type
            """, (user_id, json.dumps(new_inv), json.dumps(new_stats), new_rod))
            await db.commit()
            
    async def get_fishing_rank(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id, stats FROM fishing_data") as cursor:
                rows = await cursor.fetchall()
                
        ranking = []
        for r_uid, r_stats_json in rows:
             try:
                 s = json.loads(r_stats_json)
                 xp = s.get("xp", 0)
                 ranking.append((r_uid, xp))
             except: pass
             
        ranking.sort(key=lambda x: x[1], reverse=True)
        
        for idx, (uid, _) in enumerate(ranking, 1):
            if uid == user_id: return idx
        return len(ranking) + 1 
        
    async def get_channel_config(self, channel_id):
        return "cauca" 
