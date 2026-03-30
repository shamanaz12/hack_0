import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
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
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Copied '{filename}' to Needs_Action folder")
            
            # Optionally remove the original file from Drop_Folder after copying
            # Uncomment the next line if you want to move instead of copy
            # os.remove(file_path)
            
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error processing file {file_path}: {str(e)}")

def start_watcher(drop_folder, needs_action_folder):
    event_handler = FileHandler(drop_folder, needs_action_folder)
    observer = Observer()
    observer.schedule(event_handler, drop_folder, recursive=False)
    
    observer.start()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] File watcher started. Monitoring: {drop_folder}")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Files will be copied to: {needs_action_folder}")
    print("Press Ctrl+C to stop the watcher.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] File watcher stopped.")
    
    observer.join()

if __name__ == "__main__":
    # Define the paths
    drop_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Drop_Folder"
    needs_action_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Needs_Action"
    
    # Ensure destination folder exists
    if not os.path.exists(needs_action_folder):
        os.makedirs(needs_action_folder)
        print(f"Created destination folder: {needs_action_folder}")
    
    # Start the file watcher
    start_watcher(drop_folder, needs_action_folder)