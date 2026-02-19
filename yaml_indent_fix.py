#!/usr/bin/env python3
"""
Fix YAML indentation issues in frontmatter by parsing and reconstructing.
"""

import os
import re
import glob

def fix_yaml_indentation(filepath):
    """
    Fix YAML indentation issues by reconstructing the frontmatter properly.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Fix alt text indentation in cover block
    lines = frontmatter.split('\n')
    fixed_lines = []
    in_cover_block = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('cover:'):
            in_cover_block = True
            fixed_lines.append(line)
        elif in_cover_block and line.strip() == '':
            in_cover_block = False
            fixed_lines.append(line)
        elif in_cover_block and not line.startswith(' ') and line.strip() != '':
            if line.strip().startswith('alt:'):
                # Fix alt indentation
                fixed_lines.append('  ' + line.strip())
            else:
                in_cover_block = False
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    new_frontmatter = '\n'.join(fixed_lines)
    new_content = '---' + new_frontmatter + '---' + body
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    """
    Fix YAML indentation issues across all posts.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    post_files = glob.glob("content/posts/*.md")
    
    files_fixed = 0
    
    for filepath in post_files:
        if fix_yaml_indentation(filepath):
            files_fixed += 1
            print(f"Fixed YAML: {os.path.basename(filepath)}")
    
    print(f"\n✅ Fixed YAML indentation in {files_fixed} files.")

if __name__ == "__main__":
    main()