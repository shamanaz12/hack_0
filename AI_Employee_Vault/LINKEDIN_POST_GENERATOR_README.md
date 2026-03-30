# LinkedIn Post Draft Generator

This tool generates LinkedIn post drafts as markdown files that can be manually copied and pasted to LinkedIn. This is the safe approach to LinkedIn content creation without risking account restrictions.

## How It Works

1. The generator creates structured post drafts in markdown format
2. Each draft includes:
   - A title
   - Main content
   - Relevant hashtags
   - A call to action
   - Instructions for manual posting
3. Drafts are saved in the `LinkedIn_Drafts` folder
4. Simply copy the content from the file and paste it to LinkedIn

## Usage

### Basic Usage

Run the generator directly to create example posts:

```bash
python linkedin_post_generator.py
```

### Programmatic Usage

Import and use the generator in your own scripts:

```python
from linkedin_post_generator import LinkedInPostGenerator

generator = LinkedInPostGenerator()

# Create a custom post
generator.generate_post_draft(
    title="Your Post Title",
    content="Main content of your post goes here...",
    hashtags=["Hashtag1", "Hashtag2", "Hashtag3"],
    call_to_action="Call to action for engagement"
)
```

### AI Employee Specific Posts

The generator includes a method for creating AI Employee focused posts:

```python
generator.generate_ai_employee_update(
    topic="Your Topic",
    achievements=["Achievement 1", "Achievement 2"],
    insights=["Insight 1", "Insight 2"]
)
```

## Output

The generator creates files in the `LinkedIn_Drafts` folder with the naming convention:
`LINKEDIN_DRAFT_[timestamp]_[title].md`

Each file contains:
- The post content formatted for LinkedIn
- Hashtags
- A call to action
- Instructions for manual posting

## Why This Approach?

Direct LinkedIn automation can risk account restrictions. This safe approach:
- Generates ready-to-use content
- Maintains authentic engagement
- Allows for personal touches before posting
- Avoids potential violations of LinkedIn's terms of service

## Customization

You can customize the generator by:
- Modifying the output folder location
- Adjusting the content templates
- Adding your own post templates
- Changing the hashtag suggestions