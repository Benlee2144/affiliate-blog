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

def optimize_title(current_title):
    """Optimize title according to SEO rules."""
    # Remove quotes if present
    title = current_title.strip('"\'')
    
    # If already under 60 chars and has (2026), might be good
    if len(title) <= 60 and "(2026)" in title:
        return title
    
    # Extract product/keyword and try to create optimized version
    # This is a simplified approach - in practice, each would need manual review
    if "Review" in title:
        # Try to shorten review titles
        if "(2026):" in title:
            # Remove the colon part if too long
            base = title.split("(2026):")[0] + "(2026)"
            if len(base) <= 60:
                return base
    
    # If still too long, return original for manual review
    return title

def optimize_description(current_desc):
    """Optimize description according to SEO rules."""
    desc = current_desc.strip('"\'')
    
    # If already in good range, keep it
    if 140 <= len(desc) <= 160:
        return desc
    
    # If too long, try to trim while keeping the hook
    if len(desc) > 160:
        # Try to cut at sentence boundary
        sentences = desc.split('. ')
        if len(sentences) > 1:
            # Keep first sentence if it's long enough
            first = sentences[0] + '.'
            if len(first) >= 140:
                return first
    
    return desc

def process_post(filepath):
    """Process a single blog post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = extract_frontmatter(content)
    if not frontmatter:
        print(f"No frontmatter found in {filepath}")
        return
    
    # Extract current title and description
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    
    if not title_match or not desc_match:
        print(f"Missing title or description in {filepath}")
        return
    
    current_title = title_match.group(1)
    current_desc = desc_match.group(1)
    
    print(f"\n{'='*60}")
    print(f"FILE: {Path(filepath).name}")
    print(f"{'='*60}")
    print(f"CURRENT TITLE ({len(current_title)} chars): {current_title}")
    print(f"CURRENT DESC ({len(current_desc)} chars): {current_desc}")
    
    # Check if optimization is needed
    title_issues = []
    desc_issues = []
    
    if len(current_title) > 60:
        title_issues.append(f"TOO LONG ({len(current_title)} chars)")
    if "(2026)" not in current_title:
        title_issues.append("MISSING YEAR")
    
    if len(current_desc) < 140:
        desc_issues.append(f"TOO SHORT ({len(current_desc)} chars)")
    elif len(current_desc) > 160:
        desc_issues.append(f"TOO LONG ({len(current_desc)} chars)")
    
    if title_issues:
        print(f"TITLE ISSUES: {', '.join(title_issues)}")
    if desc_issues:
        print(f"DESC ISSUES: {', '.join(desc_issues)}")
    
    return {
        'filepath': filepath,
        'current_title': current_title,
        'current_desc': current_desc,
        'title_length': len(current_title),
        'desc_length': len(current_desc),
        'title_issues': title_issues,
        'desc_issues': desc_issues,
        'needs_optimization': bool(title_issues or desc_issues)
    }

def main():
    posts_dir = "/Users/benjaminarp/Desktop/amazon website/affiliate-blog/content/posts"
    post_files = glob.glob(os.path.join(posts_dir, "*.md"))
    
    print(f"Found {len(post_files)} posts to analyze...")
    
    results = []
    needs_optimization = []
    
    for filepath in sorted(post_files):
        result = process_post(filepath)
        if result:
            results.append(result)
            if result['needs_optimization']:
                needs_optimization.append(result)
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(needs_optimization)} out of {len(results)} posts need optimization")
    print(f"{'='*80}")
    
    return results, needs_optimization

if __name__ == "__main__":
    results, needs_opt = main()