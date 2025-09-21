import time,subprocess,os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

print("Minecraft Backuperを開始します...")

load_dotenv()

MINECRAFT_DATA_BASE = os.environ.get("MINECRAFT_DATA_PATH", "app/data")
LOG_PATH = MINECRAFT_DATA_BASE + "/logs"
WORLD_PATH = MINECRAFT_DATA_BASE + "/world"
BORG_REPO = os.environ.get("BORG_REPO_PATH", "app/repo")

# /repoディレクトリがなければ作成
if not os.path.exists(BORG_REPO):
    os.makedirs(BORG_REPO)
    print(f"Created borg repository directory at {BORG_REPO}")

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file_path):
        super().__init__()
        self.log_file = log_file_path
        subprocess.run([
            "borg", "init",
            "--encryption=none",
            BORG_REPO
            ], check=True)
        self.processed_line = ""
        print("LogHandlerの初期化を完了。")

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            print(f"{event.src_path}の変更を検出しました。")
            try:
                with open(event.src_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    recent_lines = lines[-10:]
                    for line in recent_lines:
                        if line != self.processed_lines and ("joined the game" in line.strip() or "left the game" in line.strip()):
                            print(f"ユーザーのログインを検出しました")
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            event_type = "login" if "joined the game" in line else "logout"
                            player_name = line.split(" ")[-3]
                            data_name = f"{timestamp}_{player_name}_{event_type}"

                            subprocess.run([
                                "borg", "create", "--stats", "--compression", "lz4",
                                f"{BORG_REPO}::{data_name}", WORLD_PATH,
                                "--exclude", "session.lock"
                                ])
                            print(f"バックアップ：{data_name}を作成しました。")

                            subprocess.run([
                                "borg", "prune",
                                BORG_REPO,
                                "--keep-within=24H",
                                "--keep-hourly=72",
                                "--keep-daily=7",
                                "--keep-weekly=4",
                                "--keep-monthly=3"
                                ], check=True)
                            print("古いバックアップの整理を完了しました。")
                            self.processed_line = line
                            
            except Exception as e:
                print(f"Error processing log file: {e}")

while not os.path.exists(os.path.dirname(LOG_PATH)):
    print(f" {LOG_PATH}の作成を待機中...")
    time.sleep(3)

print(f"{LOG_PATH}の監視を開始します。")
observer = Observer()
observer.schedule(LogHandler(LOG_PATH), path=LOG_PATH, recursive=False)
observer.start()
print(f"{LOG_PATH}の監視を開始しました。")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()