"""
LinkedIn Post Draft Generator
Creates markdown files with LinkedIn post drafts for manual posting
"""

import os
from datetime import datetime
from pathlib import Path

class LinkedInPostGenerator:
    def __init__(self, output_folder="LinkedIn_Drafts"):
        # Create output folder path relative to this script
        script_dir = Path(__file__).parent
        self.output_folder = script_dir / output_folder
        self.ensure_output_folder_exists()
    
    def ensure_output_folder_exists(self):
        """Create the output folder if it doesn't exist"""
        self.output_folder.mkdir(exist_ok=True)
        print(f"Output folder '{self.output_folder}' is ready.")
    
    def generate_post_draft(self, title, content, hashtags=None, call_to_action=None):
        """
        Generate a LinkedIn post draft
        
        Args:
            title (str): Title for the post draft
            content (str): Main content of the post
            hashtags (list): List of hashtags to include
            call_to_action (str): Call to action to include at the end
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not sanitized_title:
            sanitized_title = "linkedin_post"
        
        filename = f"LINKEDIN_DRAFT_{timestamp}_{sanitized_title[:50]}.md"
        filepath = os.path.join(self.output_folder, filename)
        
        # Build the post content
        post_content = f"# LinkedIn Post Draft\n\n"
        post_content += f"## {title}\n\n"
        post_content += f"{content}\n\n"
        
        if hashtags:
            hashtag_str = " ".join([f"#{tag.strip()}" for tag in hashtags if tag.strip()])
            post_content += f"{hashtag_str}\n\n"
        
        if call_to_action:
            post_content += f"**{call_to_action}**\n\n"
        
        post_content += "---\n"
        post_content += f"*Draft created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        post_content += "*To use: Copy the content above this line and paste to LinkedIn*\n"
        
        # Write the draft to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(post_content)
        
        print(f"LinkedIn post draft created: {filename}")
        print(f"Location: {filepath}")
        print(f"Content preview:\n{post_content[:200]}...\n")
        
        return filepath
    
    def generate_ai_employee_update(self, topic, achievements=None, insights=None):
        """
        Generate a specific LinkedIn post about AI Employee updates
        """
        title = f"AI Employee Update: {topic}"
        
        content = f"Exciting developments in our AI Employee project!\n\n"
        
        if achievements:
            content += f"**Recent Achievements:**\n"
            for achievement in achievements:
                content += f"- {achievement}\n"
            content += "\n"
        
        if insights:
            content += f"**Key Insights:**\n"
            for insight in insights:
                content += f"- {insight}\n"
            content += "\n"
        
        content += f"We're pushing the boundaries of what's possible with AI-assisted workflows. "
        content += f"This represents a significant step forward in our mission to enhance productivity "
        content += f"through intelligent automation."
        
        hashtags = ["AI", "ArtificialIntelligence", "Automation", "Productivity", "Innovation", "Tech"]
        call_to_action = "What are your thoughts on AI-assisted workflows? Share your perspective below! 👇"
        
        return self.generate_post_draft(title, content, hashtags, call_to_action)

# Example usage
if __name__ == "__main__":
    generator = LinkedInPostGenerator()
    
    # Example 1: Generic post
    generator.generate_post_draft(
        title="The Future of Work is Here",
        content="Our latest AI Employee prototype is demonstrating remarkable capabilities in automating routine tasks. "
               "By combining natural language processing with workflow automation, we're creating digital assistants "
               "that truly understand context and intent.",
        hashtags=["AI", "FutureOfWork", "Automation", "DigitalTransformation"],
        call_to_action="Join the conversation about the future of work! 🚀"
    )
    
    # Example 2: AI Employee specific update
    generator.generate_ai_employee_update(
        topic="Advanced Workflow Automation",
        achievements=[
            "Implemented smart task routing based on content analysis",
            "Achieved 95% accuracy in email classification",
            "Reduced manual processing time by 70%"
        ],
        insights=[
            "Context-aware automation significantly improves user satisfaction",
            "Well-designed AI assistants complement rather than replace human workers",
            "Continuous learning from user interactions enhances performance"
        ]
    )
    
    print("LinkedIn post drafts have been created in the LinkedIn_Drafts folder.")
    print("Simply copy the content from these files and paste to LinkedIn!")