#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():]
    return None, content

def update_frontmatter_field(frontmatter, field, new_value):
    """Update a specific field in YAML frontmatter."""
    # Handle quoted values
    pattern = rf'^({field}:\s*)["\']?.*["\']?$'
    replacement = f'{field}: "{new_value}"'
    updated = re.sub(pattern, replacement, frontmatter, flags=re.MULTILINE)
    return updated

def optimize_title_smart(current_title, filename):
    """Intelligently optimize title based on content and SEO rules."""
    title = current_title.strip('"\'')
    
    # Extract key information
    base_name = Path(filename).stem
    
    # Common optimization patterns
    if "Review" in title:
        # Extract product name
        if ":" in title:
            product_part = title.split(":")[0].strip()
            if "Review" in product_part and "(2026)" not in product_part:
                product_part = product_part.replace("Review", "Review (2026)")
            elif "(2026)" not in product_part:
                product_part += " (2026)"
            
            # Create hook from second part or generic
            if len(title.split(":")) > 1:
                hook_part = title.split(":", 1)[1].strip()
                if len(hook_part) > 30:
                    hook_part = "We Tested It for 30 Days"
            else:
                hook_part = "We Tested It for 30 Days"
            
            new_title = f"{product_part}: {hook_part}"
            if len(new_title) <= 60:
                return new_title
    
    # For "Best" lists
    if title.lower().startswith("best "):
        if "(2026)" not in title:
            # Try to insert year naturally
            if " 2026" in title:
                title = title.replace(" 2026", " (2026)")
            else:
                title = title + " (2026)"
        
        # If still too long, shorten
        if len(title) > 60:
            title = title.replace(" in 2026", " (2026)")
            title = title.replace(" for 2026", " (2026)")
    
    # Add year if missing
    if "(2026)" not in title and "2026" not in title:
        if len(title) < 54:  # Leave room for (2026)
            title += " (2026)"
    
    # If still too long, try aggressive shortening
    if len(title) > 60:
        # Remove common verbose phrases
        title = title.replace(" That Changes Everything", "")
        title = title.replace(" You Should Know About", "")
        title = title.replace(" We Tested Them All", "")
        title = title.replace(" (We Tested ", " (Tested ")
        title = title.replace(" Models)", ")")
        
    return title

def optimize_description_smart(current_desc):
    """Intelligently optimize description for SEO."""
    desc = current_desc.strip('"\'')
    
    # If already perfect, keep it
    if 140 <= len(desc) <= 160:
        return desc
    
    # If too long, try to trim intelligently
    if len(desc) > 160:
        # Try to cut at sentence boundaries
        sentences = desc.split('. ')
        if len(sentences) > 1:
            # Keep first sentence and see if we can add more
            result = sentences[0]
            if not result.endswith('.'):
                result += '.'
            
            # Try adding more sentences if there's room
            for i in range(1, len(sentences)):
                potential = result + " " + sentences[i]
                if not sentences[i].endswith('.') and i < len(sentences) - 1:
                    potential += '.'
                
                if len(potential) <= 160:
                    result = potential
                else:
                    break
            
            if len(result) >= 140:
                return result
    
    # If too short, we can't easily expand without context
    # Return as-is for manual review
    return desc

def process_and_fix_post(filepath):
    """Process and fix a single blog post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = extract_frontmatter(content)
    if not frontmatter:
        return False
    
    # Extract current title and description
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    
    if not title_match or not desc_match:
        return False
    
    current_title = title_match.group(1)
    current_desc = desc_match.group(1)
    
    # Optimize
    new_title = optimize_title_smart(current_title, filepath)
    new_desc = optimize_description_smart(current_desc)
    
    changes_made = False
    
    # Update if changed
    if new_title != current_title:
        frontmatter = update_frontmatter_field(frontmatter, "title", new_title)
        changes_made = True
        print(f"\nFILE: {Path(filepath).name}")
        print(f"OLD TITLE ({len(current_title)}): {current_title}")
        print(f"NEW TITLE ({len(new_title)}): {new_title}")
    
    if new_desc != current_desc:
        frontmatter = update_frontmatter_field(frontmatter, "description", new_desc)
        changes_made = True
        if not changes_made:  # Only print filename if not already printed
            print(f"\nFILE: {Path(filepath).name}")
        print(f"OLD DESC ({len(current_desc)}): {current_desc}")
        print(f"NEW DESC ({len(new_desc)}): {new_desc}")
    
    # Write back if changes were made
    if changes_made:
        new_content = f"---\n{frontmatter}\n---\n{body}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ UPDATED")
        return True
    
    return False

def main():
    posts_dir = "/Users/benjaminarp/Desktop/amazon website/affiliate-blog/content/posts"
    post_files = glob.glob(os.path.join(posts_dir, "*.md"))
    
    print(f"Starting optimization of {len(post_files)} posts...\n")
    
    updated_count = 0
    
    for filepath in sorted(post_files):
        if process_and_fix_post(filepath):
            updated_count += 1
    
    print(f"\n{'='*80}")
    print(f"OPTIMIZATION COMPLETE: {updated_count} posts were updated")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()