#!/usr/bin/env python3
"""
Fix frontmatter formatting issues where alt text got moved outside cover block.
"""

import os
import re
import glob

def fix_frontmatter_formatting(filepath):
    """
    Fix alt text that got misaligned in frontmatter.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix pattern where alt is outside cover block (multiple patterns)
    # Pattern 1: alt before caption
    pattern1 = r'(cover:\s*\n\s*image:\s*"[^"]*"\s*\n)alt:\s*"([^"]*)"(\s*\n\s*caption:)'
    replacement1 = r'\1    alt: "\2"\3'
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: alt before relative
    pattern2 = r'(cover:\s*\n\s*image:\s*"[^"]*"\s*\n)alt:\s*"([^"]*)"(\s*\n\s*relative:)'
    replacement2 = r'\1  alt: "\2"\3'
    content = re.sub(pattern2, replacement2, content)
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """
    Fix all frontmatter formatting issues.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    post_files = glob.glob("content/posts/*.md")
    
    files_fixed = 0
    
    for filepath in post_files:
        if fix_frontmatter_formatting(filepath):
            files_fixed += 1
            print(f"Fixed formatting: {os.path.basename(filepath)}")
    
    print(f"\n✅ Fixed frontmatter formatting in {files_fixed} files.")

if __name__ == "__main__":
    main()