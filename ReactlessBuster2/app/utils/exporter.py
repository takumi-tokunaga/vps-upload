import gspread, aiosqlite
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone
from utils.activity_tracker import get_last_active
from config import (
    GOOGLE_API_KEY_PATH,
    DB_PATH
    )

async def export_spread_sheet(member_list):
    # 認証情報の設定
    scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_KEY_PATH, scope)

    # APIクライアントの作成
    client = gspread.authorize(creds)
    try:
        spreadsheet = client.open("せごさばメンバー管理")
    except gspread.exceptions.SpreadsheetNotFound:
        print("スプレッドシートが見つかりません。新規作成します。")
        spreadsheet = client.create("せごさばメンバー管理")
        print("スプレッドシートを新規作成しました。")
    except Exception as e:
        print(f"スプレッドシートの取得中にエラーが発生しました: {e}")
        return

    print("スプレッドシートに接続しました")         

    member_data = []
    now = datetime.now(timezone.utc)

    for i, member in enumerate(member_list, start=0):
        try:
            sheet = spreadsheet.worksheet("サーバーメンバー")
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title="サーバーメンバー", rows="100", cols="8")
            sheet.append_row(["ID", "名前","加入日","最終アクティブ日","非アクティブ日数","告知日","キック予定日", "キック済み"])
            print("サーバーメンバーシートを作成しました")
            continue
        member_data = [[
            member["user_id"],
            member["display_name"],
            str(member["joined_at"]),
            str(member["last_active"]),
            str(member["inactive_days"]),
            str(member.get("warned_at",None)),
            str(member.get("kick_at",None)),
            member["is_kicked"]
        ]]

        sheet.update(member_data,f"A{i+2}:H{i+2}")

async def export_db(member_list):
    now = datetime.now(timezone.utc)
    async with aiosqlite.connect(DB_PATH) as db:
        print("データベースに接続しました")
        for member in member_list:
            await db.execute("""
                INSERT INTO members (user_id, display_name, joined_at, last_active, inactive_days, warned_at, kick_at, is_kicked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    joined_at = excluded.joined_at,
                    last_active = excluded.last_active,
                    inactive_days = excluded.inactive_days,
                    warned_at = excluded.warned_at,
                    kick_at = excluded.kick_at,
                    is_kicked = excluded.is_kicked
                """, 
                (member["user_id"],
                member["display_name"],
                member["joined_at"],
                member["last_active"],
                member["inactive_days"],
                member["warned_at"] if member["warned_at"] else "",
                member["kick_at"] if member["kick_at"] else "",
                1 if member["is_kicked"] else 0)
                )
            await db.commit()

async def test():    
    member_list = [
        {
            "user_id": 123456789,
            "display_name": "TestUser",
            "joined_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "last_active": datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
            "inactive_days": 30,
            "warned_at": datetime(2023, 9, 25, tzinfo=timezone.utc),
            "kick_at": datetime(2023, 10, 8, tzinfo=timezone.utc),
            "is_kicked": 0
        },
        {
            "user_id": 123436789,
            "display_name": "TestUser",
            "joined_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "last_active": datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
            "inactive_days": 30,
            "warned_at": datetime(2023, 9, 25, tzinfo=timezone.utc),
            "kick_at": datetime(2023, 10, 8, tzinfo=timezone.utc),
            "is_kicked": 0
        }
    ]
    print("testint")
    await export_spread_sheet(member_list)
    print("スプレッドシートに出力完了。")
    await export_db(member_list)
    print("データベースに出力完了。")
    print("出力完了。")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())

    