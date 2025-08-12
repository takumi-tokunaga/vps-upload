import aiosqlite
from discord.ext import commands
import sys
import os

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(DB_PATH)

    async def db_fetchall(self, query, params=()):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(query, params)
            result = await cursor.fetchall()
            await cursor.close()
            print(f"Fetched {len(result)} rows from database.")
            return result

    async def db_fetchone(self, query, params=()):
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(query, params)
            result = await cursor.fetchone()
            await cursor.close()
            print(f"Fetched one row from database: {result}")
            return result

    async def db_execute(self, query, params=()):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(query, params)
            await db.commit()
            print(f"Executed query: {query} with params: {params}")

async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))

