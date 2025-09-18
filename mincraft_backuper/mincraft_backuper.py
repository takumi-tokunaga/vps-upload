import time,subprocess,os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

MINECRAFT_DATA_BASE = os.environ.get("MINECRAFT_SERVER_JAR", "../../minecraft_data")
LOG_PATH = "/logs/latest.log"
WORLD_PATH = "/world"
BORG_REPO = "/repo"


class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.last_size = 0

    def on_modified(self, event):
        if event.src_path.endswith("latest.log"):
            try:
                with open(self.log_file, 'r') as file:
                    lines = file.readlines()
                    recent_lines = lines[-10:]
                    for line in recent_lines:
                        if "joined the game" in line or "left the game" in line:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            event_type = "login" if "joined the game" in line else "logout"
                            player_name = line.split(" ")[-3]
                            data_name = f"{str(time.time())}_{player_name}_{event_type}"

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

observer = Observer()
observer.schedule(LogHandler(LOG_PATH), path=LOG_PATH, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
                            