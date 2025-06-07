import os
import json     
import time
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class JobHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix != ".jsonl":
            return  # Ignore non-jsonl files

        print(f"[INFO] New .jsonl file detected: {file_path.name}")
        


# --------------------- MAIN ---------------------
if __name__ == "__main__":

    JOB_DIR = Path("./train_jobs1")
    JOB_DIR.mkdir(exist_ok=True)  # This ensures the folder exists

    # Set up file system watcher
    observer = Observer()
    event_handler = JobHandler()
    observer.schedule(event_handler, JOB_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()