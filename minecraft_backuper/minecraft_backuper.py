import time,subprocess,os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

print("Starting Minecraft Backuper...")

load_dotenv()

MINECRAFT_DATA_BASE = os.environ.get("MINECRAFT_DATA_PATH", "./data")
LOG_PATH = MINECRAFT_DATA_BASE + "/logs/latest.log"
WORLD_PATH = MINECRAFT_DATA_BASE + "/world"
BORG_REPO = os.environ.get("BORG_REPO_PATH", "./repo")

# /repoディレクトリがなければ作成
if not os.path.exists(BORG_REPO):
    os.makedirs(BORG_REPO)
    print(f"Created borg repository directory at {BORG_REPO}")

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.last_size = 0

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            try:
                with open(self.log_file, 'r') as file:
                    print("Log file modified, checking for player activity...")
                    lines = file.readlines()
                    recent_lines = lines[-10:]
                    for line in recent_lines:
                        if "joined the game" in line or "left the game" in line:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            event_type = "login" if "joined the game" in line else "logout"
                            player_name = line.split(" ")[-3]
                            data_name = f"{timestamp}_{player_name}_{event_type}"

                            subprocess.run([
                                "borg", "create", "--stats", "--compression", "lz4",
                                f"{BORG_REPO}::{data_name}", WORLD_PATH,
                                "--exclude", "session.lock"
                                ])
                            
                            subprocess.run([
                                "borg", "prune", "--status",
                                BORG_REPO,
                                "--keep-within=24H",
                                "--keep-hourly=72",
                                "--keep-daily=7",
                                "--keep-weekly=4",
                                "--keep-monthly=3"
                                ], check=True)
                            
                        break
            except Exception as e:
                print(f"Error processing log file: {e}")

print(f"Monitoring log file: {LOG_PATH}")
observer = Observer()
observer.schedule(LogHandler(LOG_PATH), path=LOG_PATH, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
                            