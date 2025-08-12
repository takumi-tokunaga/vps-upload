import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from datetime import date

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    print("ボットのセットアップを開始します。")
    try:
        for cog in ["database", "monitor"]:
            await bot.load_extension(f"cogs.{cog}")
            print(f" {cog}のCogをロード完了。")
    except Exception as e:
        print(f"Error loading cogs: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user.name} ({bot.user.id}としてログイン完了。")
            
bot.run(DISCORD_TOKEN)