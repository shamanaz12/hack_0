import os
import glob
import re
from datetime import datetime

def process_needs_with_approval_check():
    needs_action_dir = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Needs_Action"
    pending_approval_dir = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Pending_Approval"
    plans_dir = r"C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\Plans"
    
    # Find all .md files in Needs_Action folder
    md_files = glob.glob(os.path.join(needs_action_dir, "*.md"))
    
    if not md_files:
        print("No .md files found in Needs_Action folder.")
        return
    
    print(f"Processing {len(md_files)} .md files in Needs_Action folder:")
    
    for file_path in md_files:
        filename = os.path.basename(file_path)
        print(f"- {filename}")
        
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the content mentions email
        has_email_reference = bool(re.search(r'email|Email|EMAIL', content))
        
        # Extract title from the first line if it's a heading
        title = "Untitled Request"
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()  # Remove '# ' prefix
                break
        
        if has_email_reference:
            print(f"  -> Contains email reference. Creating approval file...")
            
            # Create an approval request file
            approval_content = f"""# Approval Request: {title}

## Request Details
From: [[{filename}]]

## Approval Required For
{title}

## Justification
{content}

## Approval Status
- [ ] Approved by Marketing Lead
- [ ] Approved by Legal
- [ ] Approved by CTO

## Additional Checks
- [ ] Email template reviewed
- [ ] Recipient list verified
- [ ] Timing confirmed
- [ ] Unsubscribe mechanism tested

## Approval Authority
- Marketing Director: [Name]
- Legal Counsel: [Name]
- CTO: [Name]

## Deadline for Approval
[{datetime.now().strftime('%Y-%m-%d')}] Request submitted
[TBD] Required by

## Notes
This request involves sending an email campaign and requires formal approval before proceeding.
"""
            
            # Create the approval file in the Pending_Approval folder
            approval_filename = f"Approval_for_{os.path.splitext(filename)[0]}.md"
            approval_path = os.path.join(pending_approval_dir, approval_filename)
            
            with open(approval_path, 'w', encoding='utf-8') as f:
                f.write(approval_content)
            
            print(f"  -> Created approval file: {approval_filename}")
        else:
            print(f"  -> No email reference. Creating plan...")
            
            # Create a plan based on the need (similar to previous script)
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
            
            print(f"  -> Created plan: {plan_filename}")
    
    print("Processing complete.")

if __name__ == "__main__":
    print(f"Checking Needs_Action files for email references...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    process_needs_with_approval_check()
    print("All files processed.")