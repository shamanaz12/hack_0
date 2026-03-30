"""
Bronze Tier File Watcher
Monitors Drop_Folder and copies new files to Bronze_Tier/inbox/
"""

import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BronzeTierFileHandler(FileSystemEventHandler):
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
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [BRONZE TIER] Copied '{filename}' -> inbox/")

        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error processing file {file_path}: {str(e)}")

def start_bronze_tier_watcher(drop_folder, bronze_inbox_folder):
    """Start file watcher for Bronze Tier"""
    event_handler = BronzeTierFileHandler(drop_folder, bronze_inbox_folder)
    observer = Observer()
    observer.schedule(event_handler, drop_folder, recursive=False)

    observer.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [BRONZE TIER] File watcher started!")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring: {drop_folder}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Files will be copied to: {bronze_inbox_folder}")
    print("[BRONZE TIER] Press Ctrl+C to stop the watcher.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] [BRONZE TIER] File watcher stopped.")

    observer.join()

if __name__ == "__main__":
    # Define the paths for Bronze Tier
    drop_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Drop_Folder"
    bronze_inbox_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Bronze_Tier\inbox"

    # Ensure destination folder exists
    if not os.path.exists(bronze_inbox_folder):
        os.makedirs(bronze_inbox_folder)
        print(f"Created Bronze Tier inbox folder: {bronze_inbox_folder}")

    # Start the file watcher for Bronze Tier
    start_bronze_tier_watcher(drop_folder, bronze_inbox_folder)
