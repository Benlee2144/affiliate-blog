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
    pattern = rf'^({field}:\s*)["\']?.*["\']?$'
    replacement = f'{field}: "{new_value}"'
    updated = re.sub(pattern, replacement, frontmatter, flags=re.MULTILINE)
    return updated

def create_optimized_title(current_title, filename):
    """Create highly optimized titles following the exact formula."""
    title = current_title.strip('"\'')
    base_name = Path(filename).stem
    
    # Product review optimization
    if "review" in title.lower():
        # Extract product name (everything before "Review")
        if "Review" in title:
            product_part = title.split("Review")[0].strip()
            if ":" in product_part:
                product_part = product_part.split(":")[0].strip()
            
            # Clean up product name
            product_part = product_part.strip(" -:")
            
            # Add year if missing
            if "(2026)" not in product_part:
                product_name = product_part.replace(" 2026", "").strip()
                optimized = f"{product_name} Review: We Tested It for 30 Days (2026)"
            else:
                product_name = product_part.replace("(2026)", "").strip()
                optimized = f"{product_name} Review: We Tested It for 30 Days (2026)"
            
            if len(optimized) <= 60:
                return optimized
    
    # Best lists optimization
    if title.lower().startswith("best "):
        # Extract the main topic
        if ":" in title:
            main_part = title.split(":")[0].strip()
        else:
            main_part = title
        
        # Add year consistently
        if "(2026)" not in main_part:
            main_part = main_part.replace(" 2026", " (2026)")
            if "(2026)" not in main_part:
                if len(main_part) < 54:
                    main_part += " (2026)"
        
        # Shorten if needed
        if len(main_part) > 60:
            # Remove verbose parts
            main_part = main_part.replace(" That Changes Everything", "")
            main_part = main_part.replace(" for Large Families", " for Families")
            main_part = main_part.replace(" and Personal Care Products", " Products")
            main_part = main_part.replace(" We Tested Them All", "")
            main_part = main_part.replace(" (We Tested ", " (Tested ")
            main_part = main_part.replace(" Models)", ")")
        
        return main_part
    
    # Comparison posts
    if " vs " in title.lower():
        if "(2026)" not in title:
            if len(title) < 54:
                title += " (2026)"
    
    # Generic optimization
    if "(2026)" not in title and "2026" not in title:
        if len(title) < 54:
            title += " (2026)"
    
    # Final length check and aggressive shortening
    if len(title) > 60:
        # Remove common verbose phrases
        replacements = [
            (" That Changes Everything", ""),
            (" You Should Know About", ""),
            (" (I Tested Them All)", ""),
            (" (We Tested ", " (Tested "),
            (" Models)", ")"),
            (" for Large Families", " for Families"),
            (" and Personal Care", ""),
            (" Actually Work", " Work"),
            (" Worth the Hype", " Worth It"),
        ]
        
        for old, new in replacements:
            title = title.replace(old, new)
            if len(title) <= 60:
                break
    
    return title

def create_optimized_description(current_desc, title):
    """Create highly optimized descriptions following the formula."""
    desc = current_desc.strip('"\'')
    
    # If already in perfect range, keep it
    if 140 <= len(desc) <= 160:
        return desc
    
    # For too long descriptions, intelligently trim
    if len(desc) > 160:
        # Try to find natural breaking points
        sentences = desc.split('. ')
        
        if len(sentences) >= 2:
            # Start with first sentence
            result = sentences[0]
            if not result.endswith('.'):
                result += '.'
            
            # Add more sentences if they fit
            for i in range(1, len(sentences)):
                sentence = sentences[i]
                if not sentence.endswith('.') and i < len(sentences) - 1:
                    sentence += '.'
                
                potential = result + " " + sentence
                if len(potential) <= 160:
                    result = potential
                else:
                    break
            
            if len(result) >= 140:
                return result
        
        # If sentence approach doesn't work, cut at word boundaries
        words = desc.split()
        result = ""
        for word in words:
            potential = result + " " + word if result else word
            if len(potential) > 160:
                break
            result = potential
        
        # Make sure we end properly
        if len(result) >= 140 and not result.endswith('.'):
            # Try to add a period if it fits
            if len(result) < 160:
                result += "."
        
        return result if len(result) >= 140 else desc
    
    # For too short descriptions, we'd need context to expand
    # Return as-is for manual review
    return desc

def process_post_comprehensive(filepath):
    """Comprehensively process and optimize a single post."""
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
    
    # Check if optimization is needed
    title_needs_fix = (
        len(current_title) > 60 or
        "(2026)" not in current_title
    )
    
    desc_needs_fix = (
        len(current_desc) < 140 or
        len(current_desc) > 160
    )
    
    if not (title_needs_fix or desc_needs_fix):
        return False
    
    changes_made = False
    filename = Path(filepath).name
    
    # Optimize title if needed
    if title_needs_fix:
        new_title = create_optimized_title(current_title, filepath)
        if new_title != current_title:
            frontmatter = update_frontmatter_field(frontmatter, "title", new_title)
            changes_made = True
            print(f"\n📝 {filename}")
            print(f"OLD TITLE ({len(current_title)}): {current_title}")
            print(f"NEW TITLE ({len(new_title)}): {new_title}")
    
    # Optimize description if needed
    if desc_needs_fix:
        new_desc = create_optimized_description(current_desc, current_title)
        if new_desc != current_desc:
            frontmatter = update_frontmatter_field(frontmatter, "description", new_desc)
            if not changes_made:
                print(f"\n📝 {filename}")
            changes_made = True
            print(f"OLD DESC ({len(current_desc)}): {current_desc}")
            print(f"NEW DESC ({len(new_desc)}): {new_desc}")
    
    # Write changes
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
    
    print(f"🔍 Analyzing {len(post_files)} posts for SEO optimization...\n")
    
    updated_count = 0
    processed_count = 0
    
    for filepath in sorted(post_files):
        processed_count += 1
        if process_post_comprehensive(filepath):
            updated_count += 1
    
    print(f"\n{'='*80}")
    print(f"🎯 FINAL OPTIMIZATION COMPLETE")
    print(f"📊 Processed: {processed_count} posts")
    print(f"✅ Updated: {updated_count} posts")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()