#!/usr/bin/env python3
"""
Final YAML fix - match alt indentation to image indentation exactly.
"""

import os
import re
import glob

def final_yaml_fix(filepath):
    """
    Match alt indentation exactly to the image field indentation.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find the pattern: cover block with image and alt
    pattern = r'(cover:\s*\n)(\s*)(image:\s*"[^"]*"\s*\n)\s*alt:\s*"([^"]*)"'
    
    def fix_indentation(match):
        cover_line = match.group(1)      # "cover:\n"
        image_indent = match.group(2)    # The whitespace before image:
        image_line = match.group(3)      # "image: ..." line
        alt_content = match.group(4)     # The alt text content
        
        # Use the same indentation as image for alt
        return f'{cover_line}{image_indent}{image_line}{image_indent}alt: "{alt_content}"'
    
    content = re.sub(pattern, fix_indentation, content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """
    Final YAML fix for all files.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    post_files = glob.glob("content/posts/*.md")
    
    files_fixed = 0
    
    for filepath in post_files:
        if final_yaml_fix(filepath):
            files_fixed += 1
            print(f"Final fix: {os.path.basename(filepath)}")
    
    print(f"\n✅ Final YAML fix applied to {files_fixed} files.")

if __name__ == "__main__":
    main()