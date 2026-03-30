"""
Bronze Tier Email Processor
Moves emails from inbox → Needs_Action → Done (manual workflow)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class BronzeTierProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.bronze_dir = self.base_dir / "Bronze_Tier"
        self.inbox_dir = self.bronze_dir / "inbox"
        self.skills_dir = self.bronze_dir / "skills"
        self.needs_action_dir = self.bronze_dir / "Needs_Action"
        self.done_dir = self.bronze_dir / "Done"
        
        # Ensure all directories exist
        for dir_path in [self.inbox_dir, self.skills_dir, self.needs_action_dir, self.done_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def process_inbox(self):
        """Move new emails from inbox to Needs_Action"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing Bronze Tier inbox...")
        
        md_files = list(self.inbox_dir.glob("*.md"))
        
        if not md_files:
            print("  No new emails in inbox.")
            return
        
        for file_path in md_files:
            filename = file_path.name
            dest_path = self.needs_action_dir / f"NA_{filename}"
            
            # Check if already processed
            if dest_path.exists():
                print(f"  Skipping {filename} - already processed")
                continue
            
            shutil.move(str(file_path), str(dest_path))
            print(f"  Moved: {filename} -> Needs_Action/")
        
        print(f"  Processed {len(md_files)} email(s)")
    
    def move_to_done(self, filename):
        """Move a completed task to Done folder"""
        source = self.needs_action_dir / filename
        if not source.exists():
            print(f"  File not found: {filename}")
            return False
        
        dest = self.done_dir / f"COMPLETED_{filename}"
        shutil.move(str(source), str(dest))
        print(f"  Moved: {filename} -> Done/")
        return True
    
    def categorize_by_skill(self, filename, category="general"):
        """Categorize a task into skills folder"""
        source = self.needs_action_dir / filename
        if not source.exists():
            print(f"  File not found: {filename}")
            return False
        
        category_dir = self.skills_dir / category
        category_dir.mkdir(exist_ok=True)
        
        dest = category_dir / filename
        shutil.copy2(str(source), str(dest))
        print(f"  Categorized: {filename} -> skills/{category}/")
        return True
    
    def show_status(self):
        """Show current status of Bronze Tier"""
        print("\n" + "="*50)
        print("  BRONZE TIER STATUS")
        print("="*50)
        
        inbox_count = len(list(self.inbox_dir.glob("*.md")))
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))
        done_count = len(list(self.done_dir.glob("*.md")))
        skills_count = len(list(self.skills_dir.rglob("*.md")))
        
        print(f"  [INBOX] inbox/           : {inbox_count} emails")
        print(f"  [WAITING] Needs_Action/  : {needs_action_count} pending")
        print(f"  [DONE] Done/             : {done_count} completed")
        print(f"  [SKILLS] skills/         : {skills_count} categorized")
        print("="*50 + "\n")

if __name__ == "__main__":
    processor = BronzeTierProcessor()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            processor.process_inbox()
        elif command == "done" and len(sys.argv) > 2:
            processor.move_to_done(sys.argv[2])
        elif command == "categorize" and len(sys.argv) > 3:
            processor.categorize_by_skill(sys.argv[2], sys.argv[3])
        elif command == "status":
            processor.show_status()
        else:
            print("Usage:")
            print("  python bronze_tier_processor.py process")
            print("  python bronze_tier_processor.py done <filename>")
            print("  python bronze_tier_processor.py categorize <filename> <category>")
            print("  python bronze_tier_processor.py status")
    else:
        processor.show_status()
