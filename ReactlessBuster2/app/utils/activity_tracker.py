from datetime import timezone

async def get_last_active(member, joined_at, messages, threads=None, forums=None):
    last_active = joined_at.replace(tzinfo=timezone.utc)

    # 通常メッセージ
    for msg in messages:
        if msg.author == member:
            last_active = max(last_active, msg.created_at.replace(tzinfo=timezone.utc))
        for reaction in msg.reactions:
            async for user in reaction.users():
                if user == member:
                    last_active = max(last_active, msg.created_at.replace(tzinfo=timezone.utc))

    # スレッドメッセージ
    if threads:
        for tmsg in threads:
            if tmsg.author == member:
                last_active = max(last_active, tmsg.created_at.replace(tzinfo=timezone.utc))
            for reaction in tmsg.reactions:
                async for user in reaction.users():
                    if user == member:
                        last_active = max(last_active, tmsg.created_at.replace(tzinfo=timezone.utc))

    # フォーラムメッセージ
    if forums:
        for fmsg in forums:
            if fmsg.author == member:
                last_active = max(last_active, fmsg.created_at.replace(tzinfo=timezone.utc))
            for reaction in fmsg.reactions:
                async for user in reaction.users():
                    if user == member:
                        last_active = max(last_active, fmsg.created_at.replace(tzinfo=timezone.utc))
    
    return last_active
