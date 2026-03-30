import os
import glob
from datetime import datetime

def process_needs_action_files():
    needs_action_dir = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Needs_Action"
    plans_dir = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Plans"
    
    # Find all .md files in Needs_Action folder
    md_files = glob.glob(os.path.join(needs_action_dir, "*.md"))
    
    if not md_files:
        print("No .md files found in Needs_Action folder.")
        return
    
    print(f"Found {len(md_files)} .md files in Needs_Action folder:")
    
    for file_path in md_files:
        filename = os.path.basename(file_path)
        print(f"- {filename}")
        
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from the first line if it's a heading
        title = "Untitled Plan"
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()  # Remove '# ' prefix
                break
        
        # Create a plan based on the need
        plan_content = f"""# Plan: {title}

## Overview
This plan addresses the need described in [[{filename}]].

## Objective
To implement the requested functionality as described in the original request.

## Tasks
- [ ] Analyze requirements in detail
- [ ] Design system architecture
- [ ] Implement core functionality
- [ ] Test implementation
- [ ] Document the solution
- [ ] Deploy to production

## Timeline
- Analysis: Day 1
- Design: Day 2
- Implementation: Days 3-7
- Testing: Days 8-9
- Documentation: Day 10
- Deployment: Day 11

## Resources Required
- 1 Senior Developer
- 1 QA Engineer
- Access to development environment
- Testing resources

## Dependencies
- Original request: [[{filename}]]
- System requirements
- Available development resources

## Success Criteria
- Requirement from [[{filename}]] is fully addressed
- Solution meets quality standards
- Delivered on time
- Properly documented

## Notes
Generated automatically based on the need described in [[{filename}]].
"""
        
        # Create the plan file in the Plans folder
        plan_filename = f"Plan_for_{os.path.splitext(filename)[0]}.md"
        plan_path = os.path.join(plans_dir, plan_filename)
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        print(f"Created plan: {plan_filename}")

if __name__ == "__main__":
    print(f"Processing files in Needs_Action folder...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    process_needs_action_files()
    print("Processing complete.")