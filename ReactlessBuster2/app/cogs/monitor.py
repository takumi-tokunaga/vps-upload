from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import discord
from datetime import date

from config import (
    INACTIVE_DAYS_THRESHOLD,
    WARNING_GRACE_DAYS,
    MESSAGE_CHANNEL,
    GUILD_ID,
    REJOIN_LINK
)

from utils.activity_tracker import get_last_active
from utils.server_cacher import cache_server
from utils.exporter import export_spread_sheet, export_db
from utils.sync_to_django import sync_member_to_django

class MonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.get_cog("DatabaseCog")
        print("MonitorCogを初期化しました。")
        self.check_inactive.start()  # ループタスクを開始

    def cog_unload(self):
        self.check_inactive.cancel()

    @tasks.loop(hours=24)
    async def check_inactive(self):
        row = await self.db.db_fetchone("SELECT last_checked FROM check_log WHERE id = 1")
        today = date.today().isoformat()
        if row[0] == today:
            print("本日はすでにチェック済みです。")
            return
        print("本日のチェックを開始します。")
        await self.check_inactive_task()

    async def check_inactive_task(self):
        print("check_inactive_taskを実行中...")
        await self.bot.wait_until_ready()
        print("check_inactive_taskが動作開始...")
        now = datetime.now(timezone.utc)
        guild = self.bot.get_guild(GUILD_ID)

        if not guild:
            print(f"サーバーが見つかりません。GUILD_ID:{GUILD_ID}。処理を中断します。")
            print("Botが接続されているサーバー:", [g.id for g in self.bot.guilds])
            await self.bot.close()
            return
        else:
            print(f"{guild.name}に接続しました")

        warning_channel = discord.utils.get(guild.text_channels, name=MESSAGE_CHANNEL)
        if not warning_channel:
            print(f"警告チャンネル:{MESSAGE_CHANNEL}が見つかりません。処理を中断します。")
            await self.bot.close()
            return

        message_cache, thread_cache, forum_cache = await cache_server(guild)
        member_list = []
                    
        for member in guild.members:
            if member.bot:
                print(f"{member.name}はボットのためスキップします。")
                continue
            print(f"{member.name}のチェックを開始...[{len(member_list)+1} / {len(guild.members)}]")
            joined_at = member.joined_at.replace(tzinfo=timezone.utc)
            last_active = await get_last_active(member, joined_at, message_cache, thread_cache, forum_cache)
            inactive_days = (now - last_active).days
            print(f"{member.name}の非アクティブ日数: {inactive_days}")

            row = await self.db.db_fetchone("SELECT * FROM inactive_members WHERE user_id = ?", (member.id,)) #警告リストを確認

            if row: #告知リストに登録がある場合
                print(row)
                uid = row[0]
                warned_at = datetime.fromisoformat(row[1])
                kick_at = datetime.fromisoformat(row[2])
                print(f"{member.name}はすでに非アクティブとして記録されています: 告知日{warned_at.date()},キック予定日 {kick_at.date()}")
                if last_active > warned_at: #告知後に活動が確認された場合
                    print(f"{member.name}を告知リストから除外")
                    await self.bot.get_cog("DatabaseCog").db_execute("DELETE FROM inactive_members WHERE user_id = ?", (uid,))
                    await warning_channel.send(f"{member.mention}さんは告知後の活動を確認したため、告知リストから除外されました")
                elif now >= kick_at: #キック予定日を過ぎている場合
                    print(f"{member.name}をキック")
                    await self.db.db_execute("UPDATE members SET is_kicked = 1 WHERE user_id = ?",(uid,))
                    await self.db.db_execute("DELETE FROM inactive_members WHERE user_id = ?", (uid,))
                    
                    await guild.kick(member, reason="非アクティブ")
                    try:
                        await member.send(f"Reactless busterにより{guild.name}からキックされました。サーバーへの再加入はいつでも大歓迎です。下記リンクからご参加ください。")
                        await member.send(REJOIN_LINK)
                        await warning_channel.send(f"⚠️{member.name} を非アクティブのためキックしました")
                    except discord.Forbidden:
                        print(f"DM送信失敗: {member.name} はDMを拒否しています")
                        await warning_channel.send(f"⚠️{member.display_name} を非アクティブのためキックしました。DM送信は失敗しました。")

            else: #告知リストに登録がない場合
                if inactive_days >= INACTIVE_DAYS_THRESHOLD: #告知リストに登録がなく、非アクティブ日数が閾値を超えた場合
                    print(f"{member.name}は{inactive_days}日間非アクティブ。告知リストに追加")
                    warned_at = now.isoformat()
                    kick_at = (now + timedelta(days=WARNING_GRACE_DAYS)).isoformat()
                    await self.db.db_execute("INSERT INTO inactive_members (user_id, warned_at, kick_at) VALUES (?, ?, ?)",
                                        (member.id, warned_at, kick_at))
                    await warning_channel.send(f"{member.mention}さんの非アクティブ日数が{inactive_days}日です。{WARNING_GRACE_DAYS}日以内に活動がない場合、サーバーから退出となります。")     
                else:
                    print(f"{member.name}は{inactive_days}日非アクティブ。告知リストに追加しません")      
            
            member_list.append({
                "user_id": member.id,
                "display_name": member.display_name,
                "joined_at": member.joined_at.isoformat(),
                "last_active": last_active.isoformat(),
                "inactive_days": inactive_days,
                "warned_at": warned_at if 'warned_at' in locals() else None,
                "kick_at": kick_at if 'kick_at' in locals() else None,
                "is_kicked": 0
            })
 
            """
            await sync_member_to_django({
                "user_id": member.id,
                "display_name": member.display_name,
                "joined_at": member.joined_at.isoformat(),
                "last_active": last_active.isoformat(),
                "inactive_days": inactive_days,
                "warned_at": warned_at if 'warned_at' in locals() else None,
                "kick_at": kick_at if 'kick_at' in locals() else None,
                "is_kicked": 0
            })
            """
                    
                           
        print(member_list)
        print("スプレッドシートとデータベースに出力。")
        await export_spread_sheet(member_list)
        print("スプレッドシートに出力完了。")
        await export_db(member_list)
        print("membersテーブルに出力完了。")
        today = date.today().isoformat()
        await self.db.db_execute(
                "INSERT INTO check_log (id, last_checked) VALUES (1, ?)"
                "ON CONFLICT(id) DO UPDATE SET last_checked = ?",
                (today, today)
            )
        print("check_logに本日のチェックを記録完了。") 
        print(f"{guild.name}メンバーのチェックが完了しました。")
        return
    
async def setup(bot):
    await bot.add_cog(MonitorCog(bot))