#!/usr/bin/env python3
"""
Needs Action Analyzer - Creates plan.md files for all files in Needs_Action folders
Analyzes each file and creates a corresponding plan in the Plans folder
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Try to import qwen SDK
try:
    from dashscope import Generation
    import dashscope
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False


class NeedsActionAnalyzer:
    """Analyzes files in Needs_Action folders and creates plan.md files"""
    
    def __init__(self, vault_path: Path, api_key: str = None):
        self.vault_path = vault_path
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        self.plans_folder = vault_path / 'Plans'
        self.plans_folder.mkdir(exist_ok=True)
        
        # Initialize Qwen API
        if QWEN_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key
        
        self.analyzed_count = 0
        self.failed_count = 0
    
    def find_needs_action_folders(self) -> List[Path]:
        """Find all Needs_Action folders in the vault"""
        needs_action_folders = []
        
        # Common patterns for Needs_Action folders
        patterns = [
            '**/Needs_Action',
            '**/Silver_Tier/Needs_Action',
            '**/Bronze_Tier/Needs_Action',
            'AI_Employee_Vault/**/Needs_Action'
        ]
        
        for pattern in patterns:
            folders = self.vault_path.glob(pattern)
            for folder in folders:
                if folder.is_dir() and folder not in needs_action_folders:
                    needs_action_folders.append(folder)
        
        # Also check specific known paths
        known_paths = [
            self.vault_path / 'AI_Employee_Vault' / 'Needs_Action',
            self.vault_path / 'AI_Employee_Vault' / 'Silver_Tier' / 'Needs_Action',
            self.vault_path / 'AI_Employee_Vault' / 'Bronze_Tier' / 'Needs_Action',
        ]
        
        for path in known_paths:
            if path.exists() and path.is_dir() and path not in needs_action_folders:
                needs_action_folders.append(path)
        
        return needs_action_folders
    
    def get_files_to_analyze(self, folders: List[Path]) -> List[Path]:
        """Get all markdown files from Needs_Action folders"""
        files = []
        for folder in folders:
            for file in folder.glob('*.md'):
                if file not in files:
                    files.append(file)
        return files
    
    def read_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse markdown file with frontmatter"""
        content = file_path.read_text(encoding='utf-8')
        
        # Parse YAML frontmatter
        metadata = {}
        body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                
                # Simple YAML parsing
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        metadata[key] = value
        
        return {
            'path': str(file_path),
            'name': file_path.stem,
            'metadata': metadata,
            'body': body.strip(),
            'full_content': content
        }
    
    def analyze_with_ai(self, file_data: Dict) -> str:
        """Use Qwen API to analyze file and generate plan"""
        prompt = f"""Analyze this task file and create a detailed action plan.

## File: {file_data['name']}

## Metadata:
{json.dumps(file_data['metadata'], indent=2)}

## Content:
{file_data['body'][:2000]}

## Task:
Create a detailed plan.md file with:
1. Clear objective
2. Step-by-step action items
3. Required resources
4. Estimated timeline
5. Success criteria
6. Potential obstacles

Format as markdown with checkboxes for action items.
"""
        
        if QWEN_AVAILABLE and self.api_key:
            try:
                response = Generation.call(
                    model='qwen-plus',
                    prompt=prompt,
                    result_format='message'
                )
                
                if response.status_code == 200:
                    return response.output.choices[0].message.content
            except Exception as e:
                print(f"  API error: {e}")
        
        # Fallback: Generate simple plan without AI
        return self._generate_simple_plan(file_data)
    
    def _generate_simple_plan(self, file_data: Dict) -> str:
        """Generate a simple plan without AI"""
        metadata = file_data['metadata']
        
        plan = f"""# Action Plan: {file_data['name']}

## Objective
Process and complete the task from: `{file_data['name']}`

## Analysis

### Metadata
"""
        
        for key, value in metadata.items():
            plan += f"- **{key}**: {value}\n"
        
        plan += f"""
## Action Items

- [ ] Review the source file content
- [ ] Identify required actions
- [ ] Gather necessary resources
- [ ] Execute the task
- [ ] Verify completion
- [ ] Move to Done folder

## Timeline
- **Started**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Estimated Duration**: 1-2 hours
- **Priority**: {metadata.get('priority', 'normal')}

## Resources Needed
- Access to required tools/systems
- Any relevant documentation
- Time allocation for task completion

## Success Criteria
- [ ] All action items completed
- [ ] Quality check passed
- [ ] Output saved to appropriate location
- [ ] Status updated

## Notes
Add any additional notes or observations here.

---
*Generated by Needs Action Analyzer*
*Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return plan
    
    def create_plan_file(self, file_data: Dict, plan_content: str) -> Path:
        """Create plan.md file in Plans folder"""
        # Create plan file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_filename = f"plan_{file_data['name']}_{timestamp}.md"
        plan_path = self.plans_folder / plan_filename
        
        # Add frontmatter
        frontmatter = f"""---
metadata:
  source_file: "{file_data['path']}"
  source_name: "{file_data['name']}"
  created: "{datetime.now().isoformat()}"
  analyzer: "Needs Action Analyzer"
  priority: "{file_data['metadata'].get('priority', 'normal')}"
---

"""
        full_content = frontmatter + plan_content
        
        # Write plan file
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return plan_path
    
    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all files in all Needs_Action folders"""
        print("=" * 60)
        print("Needs Action Analyzer")
        print("=" * 60)
        
        # Find all Needs_Action folders
        folders = self.find_needs_action_folders()
        print(f"\nFound {len(folders)} Needs_Action folder(s):")
        for folder in folders:
            print(f"  - {folder}")
        
        # Get all files to analyze
        files = self.get_files_to_analyze(folders)
        print(f"\nFound {len(files)} file(s) to analyze")
        
        if not files:
            print("\nNo files found to analyze!")
            return {'analyzed': 0, 'failed': 0, 'plans': []}
        
        results = {
            'analyzed': 0,
            'failed': 0,
            'plans': []
        }
        
        # Analyze each file
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Analyzing: {file_path.name}")
            
            try:
                # Read file content
                file_data = self.read_file_content(file_path)
                print(f"  Metadata found: {len(file_data['metadata'])} fields")
                
                # Analyze with AI
                print("  Generating plan...")
                plan_content = self.analyze_with_ai(file_data)
                
                # Create plan file
                plan_path = self.create_plan_file(file_data, plan_content)
                print(f"  [OK] Plan created: {plan_path.name}")
                
                results['analyzed'] += 1
                results['plans'].append({
                    'source': str(file_path),
                    'plan': str(plan_path)
                })
                
            except Exception as e:
                print(f"  [ERROR] Error: {e}")
                results['failed'] += 1
                self.failed_count += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("Analysis Complete")
        print("=" * 60)
        print(f"Files analyzed: {results['analyzed']}")
        print(f"Failed: {results['failed']}")
        print(f"Plans created: {len(results['plans'])}")
        print(f"Plans folder: {self.plans_folder}")
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Needs_Action files and create plans')
    parser.add_argument('--vault', type=str, default=None, help='Path to vault folder')
    parser.add_argument('--api-key', type=str, default=None, help='Qwen API key')
    args = parser.parse_args()
    
    # Determine vault path
    vault_path = Path(args.vault) if args.vault else Path.cwd()
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create analyzer
    analyzer = NeedsActionAnalyzer(vault_path, args.api_key)
    
    # Run analysis
    results = analyzer.analyze_all()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
