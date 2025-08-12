import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# 環境変数をロード
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# Discord設定
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKENが設定されていません。.envファイルを確認してください。")
    sys.exit(1)
GUILD_ID = int(os.getenv("GUILD_ID"))  # デフォルトのGUILD_IDを設定

# 監視設定
INACTIVE_DAYS_THRESHOLD = int(os.getenv("INACTIVE_DAYS_THRESHOLD", 30))
WARNING_GRACE_DAYS = int(os.getenv("WARNING_GRACE_DAYS", 10))

# Discord チャンネル設定
MESSAGE_CHANNEL = os.getenv("MESSAGE_CHANNEL", "bot-message")
REJOIN_LINK = os.getenv("REJOIN_LINK", "https://discord.gg/VdFS7DWhYZ")

# データベース設定
DB_NAME = os.getenv("DB_FILE", "members.db")
DB_PATH = BASE_DIR / "db" / DB_NAME

# Google API設定
GOOGLE_API_KEY_FILE = os.getenv("GOOGLE_API_KEY_FILE", "reactlessbuster-23942964bf98.json")
GOOGLE_API_KEY_PATH = BASE_DIR / "credentials" / GOOGLE_API_KEY_FILE

# ディレクトリ設定
LOGS_DIR = BASE_DIR / "logs"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# 設定値の検証
def validate_config():
    """設定値が正しいかチェック"""
    errors = []
    
    if not DISCORD_TOKEN:
        errors.append("DISCORD_TOKEN が設定されていません")
        sys.exit(1)
        
    if not GUILD_ID:
        errors.append("GUILD_ID が設定されていません")
        sys.exit(1)
        
    if not GOOGLE_API_KEY_PATH.exists():
        errors.append(f"Google APIキーファイルが見つかりません: {GOOGLE_API_KEY_PATH}")
        sys.exit(1)
    
    if INACTIVE_DAYS_THRESHOLD <= 0:
        errors.append("INACTIVE_DAYS_THRESHOLD は正の値である必要があります")
    
    if WARNING_GRACE_DAYS <= 0:
        errors.append("WARNING_GRACE_DAYS は正の値である必要があります")
    
    if errors:
        print("❌ 設定エラー:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True