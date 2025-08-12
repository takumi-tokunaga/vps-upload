import logging
import os
from datetime import datetime

def setup_logging():
    """ログの設定を行う"""
    
    # logsフォルダが存在しない場合は作成
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # ログファイル名（日付付き）
    log_filename = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
    
    # ログフォーマット
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # コンソールにも出力
        ]
    )
    
    # Discordライブラリのログレベルを調整
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
