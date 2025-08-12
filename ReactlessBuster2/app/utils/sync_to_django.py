import aiohttp

async def sync_member_to_django(member_data):
    async with aiohttp.ClientSession() as session:
        await session.post("http://localhost:8000/api/update_activity/", json=member_data)