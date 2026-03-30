"""
Silver Tier File Watcher
Monitors Drop_Folder and copies new files to Silver_Tier/inbox/
"""

import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SilverTierFileHandler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder):
        self.source_folder = source_folder
        self.destination_folder = destination_folder

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.process_file(event.dest_path)

    def process_file(self, file_path):
        try:
            filename = os.path.basename(file_path)
            destination_path = os.path.join(self.destination_folder, filename)

            # Handle duplicate filenames by adding a counter
            counter = 1
            name, ext = os.path.splitext(filename)
            while os.path.exists(destination_path):
                new_filename = f"{name}_{counter}{ext}"
                destination_path = os.path.join(self.destination_folder, new_filename)
                counter += 1

            shutil.copy2(file_path, destination_path)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SILVER TIER] Copied '{filename}' -> inbox/")

        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error processing file {file_path}: {str(e)}")

def start_silver_tier_watcher(drop_folder, silver_inbox_folder):
    """Start file watcher for Silver Tier"""
    event_handler = SilverTierFileHandler(drop_folder, silver_inbox_folder)
    observer = Observer()
    observer.schedule(event_handler, drop_folder, recursive=False)

    observer.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SILVER TIER] File watcher started!")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring: {drop_folder}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Files will be copied to: {silver_inbox_folder}")
    print("[SILVER TIER] Press Ctrl+C to stop the watcher.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] [SILVER TIER] File watcher stopped.")

    observer.join()

if __name__ == "__main__":
    # Define the paths for Silver Tier
    drop_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Drop_Folder"
    silver_inbox_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Silver_Tier\inbox"

    # Ensure destination folder exists
    if not os.path.exists(silver_inbox_folder):
        os.makedirs(silver_inbox_folder)
        print(f"Created Silver Tier inbox folder: {silver_inbox_folder}")

    # Start the file watcher for Silver Tier
    start_silver_tier_watcher(drop_folder, silver_inbox_folder)
