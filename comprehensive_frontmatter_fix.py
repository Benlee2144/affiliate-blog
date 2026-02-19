#!/usr/bin/env python3
"""
Comprehensive frontmatter fix for all alt text positioning issues.
"""

import os
import re
import glob

def comprehensive_fix_frontmatter(filepath):
    """
    Fix all possible alt text positioning issues in frontmatter.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find cover block and fix alt positioning
    # Pattern: cover block with potential misaligned alt
    cover_pattern = r'cover:\s*\n((?:\s+[^:\n]+:[^\n]*\n)*?)alt:\s*"([^"]*)"((?:\s*\n\s*[^:\n]+:[^\n]*)*)'
    
    def fix_alt_position(match):
        cover_start = match.group(1)  # Everything after cover: until alt:
        alt_content = match.group(2)  # The alt text content
        rest_content = match.group(3)  # Everything after alt
        
        # Remove alt from rest_content if it exists
        rest_content_clean = rest_content.strip()
        
        # Reconstruct with properly indented alt
        result = f"cover:\n{cover_start}    alt: \"{alt_content}\"{rest_content}"
        return result
    
    content = re.sub(cover_pattern, fix_alt_position, content, flags=re.MULTILINE)
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """
    Fix all frontmatter formatting issues comprehensively.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    post_files = glob.glob("content/posts/*.md")
    
    files_fixed = 0
    
    for filepath in post_files:
        if comprehensive_fix_frontmatter(filepath):
            files_fixed += 1
            print(f"Fixed: {os.path.basename(filepath)}")
    
    print(f"\n✅ Comprehensively fixed frontmatter in {files_fixed} files.")

if __name__ == "__main__":
    main()