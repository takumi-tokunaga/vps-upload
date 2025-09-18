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

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            try:
                os.path.getsize(self.log_file)
                with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as file:
                    print("Log file modified, checking for player activity...")
                    print(f"opened file path: {self.log_file}")
                    lines = file.readlines()
                    print(f"readed lines: {lines}")
                    recent_lines = lines[-20:]
                    print(f"recent lines: {recent_lines}")
                    for line in recent_lines:
                        print(f"Checking line: {line.strip()}")
                        if "joined the game" in line.strip() or "left the game" in line.strip():
                            print("Detected player activity")
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            event_type = "login" if "joined the game" in line else "logout"
                            player_name = line.split(" ")[-3]
                            data_name = f"{timestamp}_{player_name}_{event_type}"

                            subprocess.run([
                                "borg", "create", "--stats", "--compression", "lz4",
                                f"{BORG_REPO}::{data_name}", WORLD_PATH,
                                "--exclude", "session.lock"
                                ])
        
                            print("Created backup")
                            
                            subprocess.run([
                                "borg", "prune", "--status",
                                BORG_REPO,
                                "--keep-within=24H",
                                "--keep-hourly=72",
                                "--keep-daily=7",
                                "--keep-weekly=4",
                                "--keep-monthly=3"
                                ], check=True)                           
                        else:
                            print("No player join/leave events detected in recent log lines.")
            except Exception as e:
                print(f"Error processing log file: {e}")


# サーバーが起動してログファイルに内容が書き込まれるまで待機
while not (os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 0):
    print("Waiting for server to start and log file to be written...")
    time.sleep(2)

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
                            