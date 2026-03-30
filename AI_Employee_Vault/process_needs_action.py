import os
import shutil
import glob
from datetime import datetime

def process_needs_action_file(file_path):
    """
    Process a file from Needs_Action folder according to the specified workflow:
    1. Create a structured Plan.md
    2. Break into actionable steps
    3. Add status tracking
    4. Log reasoning summary
    5. Move original file to Plans folder
    """
    
    # Extract file information
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    
    # Define folder paths
    plans_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Plans"
    needs_action_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Needs_Action"
    
    # Ensure Plans folder exists
    if not os.path.exists(plans_folder):
        os.makedirs(plans_folder)
        
    # Read the original file content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Create structured Plan.md content
    plan_content = f"""# Plan: {filename_without_ext}

## Reasoning Summary
Processed from original request in Needs_Action folder on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

## Original Request
```
{original_content[:500]}{'...' if len(original_content) > 500 else ''}
```

## Actionable Steps
- [ ] Analyze requirements from original request
- [ ] Break down into specific tasks
- [ ] Assign priorities and deadlines
- [ ] Execute planned actions
- [ ] Verify completion criteria
- [ ] Document outcomes

## Status Tracking
- [ ] Initial assessment
- [ ] Requirement analysis
- [ ] Task breakdown
- [ ] Execution phase
- [ ] Verification
- [ ] Completion

## Next Steps
1. Review original request details
2. Create detailed task list
3. Set timeline and milestones
4. Begin execution
5. Update status regularly
"""

    # Write the Plan.md file in the Plans folder
    plan_file_path = os.path.join(plans_folder, f"{filename_without_ext}_Plan.md")
    with open(plan_file_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    print(f"Created Plan: {plan_file_path}")
    
    # Move original file to Plans folder
    destination_path = os.path.join(plans_folder, filename)
    shutil.move(file_path, destination_path)
    
    print(f"Moved original file to Plans: {destination_path}")
    
    return plan_file_path, destination_path

def process_all_needs_action():
    """
    Process all files in the Needs_Action folder
    """
    needs_action_folder = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Needs_Action"
    
    # Find all files in Needs_Action folder
    files = glob.glob(os.path.join(needs_action_folder, "*"))
    
    if not files:
        print("No files found in Needs_Action folder to process.")
        return
    
    print(f"Processing {len(files)} files from Needs_Action folder...")
    
    for file_path in files:
        if os.path.isfile(file_path):
            print(f"Processing: {os.path.basename(file_path)}")
            try:
                plan_path, moved_path = process_needs_action_file(file_path)
                print(f"Successfully processed: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    print("Finished processing all files in Needs_Action folder.")

if __name__ == "__main__":
    print("Starting processing of Needs_Action files...")
    process_all_needs_action()
    print("Processing complete!")