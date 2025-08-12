import aiosqlite
import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))
from config import DB_PATH, validate_config

async def init_db():
    """データベースとテーブルを初期化する"""
    
    # 設定の検証
    if not validate_config():
        print("❌ 設定エラーのため、データベース初期化を中止します")
        return False
    
    try:
        # dbフォルダがなければ作成
        os.makedirs(DB_PATH.parent, exist_ok=True)

        async with aiosqlite.connect(DB_PATH) as db:
            # メンバーテーブル
            await db.execute("""
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                display_name TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                inactive_days INTEGER NOT NULL,
                warned_at TEXT,
                kick_at TEXT,
                is_kicked INTEGER DEFAULT 0
            )
            """)
            
            # 非アクティブメンバーテーブル
            await db.execute("""
            CREATE TABLE IF NOT EXISTS inactive_members (
                user_id INTEGER PRIMARY KEY,
                warned_at TEXT,
                kick_at TEXT
            )
            """)
            
            # チェックログテーブル
            await db.execute("""
            CREATE TABLE IF NOT EXISTS check_log (
                id INTEGER PRIMARY KEY,
                last_checked TEXT
            )
            """)
            
            await db.commit()
            print("✅ データベースが初期化されました")
            print(f"📁 データベースファイル: {DB_PATH}")
            return True
            
    except Exception as e:
        print(f"❌ データベース初期化エラー: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(init_db())