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

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file_path):
        super().__init__()
        self.log_file = log_file_path
        self.processed_line = []

        # /repoディレクトリがなければ作成
        if not os.path.exists(BORG_REPO):
            os.makedirs(BORG_REPO)
            print(f"Created borg repository directory at {BORG_REPO}")

        # borgリポジトリの初期化または信用プロセス
        if not os.path.exists(os.path.join(BORG_REPO, 'config')):
            subprocess.run([
                "borg", "init", "--encryption=none", BORG_REPO
            ], check=True)
            print("Borgリポジトリの初期化を完了しました。")
        else:
            """
            subprocess.run([
                "borg", "config", BORG_REPO, "--append-only", "0"
            ], check=True)
            """
            print("Borgリポジトリがすでに存在します。信用プロセスを完了しました。")

        print("LogHandlerの初期化を完了。")


    def on_modified(self, event): # 監視対象のファイルが変更されたときに呼ばれる
        if event.src_path.endswith("latest.log"):
            try:
                with open(event.src_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    recent_lines = lines[-10:]
                    for line in recent_lines:
                        if line not in self.processed_line and ("joined the game" in line.strip() or "left the game" in line.strip()):
                            print(f"ユーザーの出入りを検出しました")
                            print(line)
                            self.backup_world(line)
                            self.processed_line.append(line)
                            if len(self.processed_line) > 10:
                                self.processed_line.pop(0)
            except Exception as e:
                print(f"Error processing log file: {e}")


    def backup_world(self, line):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        event_type = "login" if "joined the game" in line else "logout"

        parts = line.split(":")
        if len(parts) > 1:
            msg = parts[-1].strip()
            if "joined the game" in msg:
                player_name = msg.replace("joined the game", "").strip()
            elif "left the game" in msg:
                player_name = msg.replace("left the game", "").strip()
            else:
                player_name = "unknown"
        else:
            player_name = "unknown"

        data_name = f"{timestamp}_{player_name}_{event_type}"

        try:
            result = subprocess.run([
                "borg", "create",
                "--stats", "--compression", "lz4",
                f"{BORG_REPO}::{data_name}", WORLD_PATH,
                "--exclude", "session.lock"
            ], check=True, capture_output=True, text=True)
            print(f"バックアップ：{data_name}を作成しました。\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"borg create error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")

        try:
            result = subprocess.run([
                "borg", "prune",
                BORG_REPO,
                "--keep-hourly=24",
                "--keep-daily=7",
                "--keep-weekly=4",
                "--keep-monthly=3"
            ], check=True, capture_output=True, text=True)
            print(f"古いバックアップの整理を完了しました。\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"borg prune error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")

        try:
            result = subprocess.run([
                "borg", "compact",
                BORG_REPO
            ], check=True, capture_output=True, text=True)
            print(f"リポジトリの圧縮を完了しました。\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"borg compact error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")

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