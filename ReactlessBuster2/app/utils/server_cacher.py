from datetime import datetime, timezone, timedelta
import discord

async def cache_server(guild):
    message_cache = []
    thread_cache = []
    forum_cache = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=35)
    for channel in guild.text_channels:
        try:
            messages = [msg async for msg in channel.history(after=cutoff)]
            for msg in messages:
                    message_cache.append(msg)
        except Exception as e:
            print(f"{channel.name} で履歴取得エラー: {e}")

    for thread in guild.threads:
            try:
                messages = [msg async for msg in thread.history(after=cutoff)]
                for msg in messages:
                    thread_cache.append(msg)
            except Exception as e:
                print(f"{thread.name} でスレッド履歴取得エラー: {e}")
    
    for channel in guild.channels:
        if isinstance(channel, discord.ForumChannel):
            for thread in channel.threads:
                try:
                    messages = [msg async for msg in thread.history(after=cutoff)]
                    for msg in messages:
                        forum_cache.append(msg)
                except Exception as e:
                    print(f"{thread.name} でフォーラムスレッド履歴取得エラー: {e}")

    return message_cache, thread_cache, forum_cache