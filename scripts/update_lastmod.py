#!/usr/bin/env python3
"""
Update lastmod dates in Hugo front matter for modified posts.
Run this before committing changes to ensure Google sees fresh content.

Usage:
    python update_lastmod.py [--all]
    
    --all: Update all posts (useful for bulk refresh)
    Default: Only updates posts modified in git
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
import subprocess

CONTENT_DIR = Path(__file__).parent.parent / "content" / "posts"


def get_modified_posts() -> list:
    """Get list of posts modified in git but not yet committed."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            cwd=CONTENT_DIR.parent.parent
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.md') and 'content/posts/' in f]
    except Exception:
        return []


def update_lastmod(filepath: Path) -> bool:
    """Update the lastmod date in a post's front matter."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        if not content.startswith('---'):
            return False
            
        # Find the end of front matter
        end = content.find('---', 3)
        if end < 0:
            return False
            
        front_matter = content[3:end]
        body = content[end+3:]
        
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        
        # Update or add lastmod
        if 'lastmod:' in front_matter:
            front_matter = re.sub(
                r'lastmod:\s*[\d\-T:+Z]+',
                f'lastmod: {now}',
                front_matter
            )
        else:
            # Add after date line
            front_matter = re.sub(
                r'(date:\s*[\d\-T:+Z]+)',
                f'\\1\nlastmod: {now}',
                front_matter
            )
        
        # Write back
        new_content = f'---{front_matter}---{body}'
        filepath.write_text(new_content, encoding='utf-8')
        
        return True
        
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False


def main():
    update_all = '--all' in sys.argv
    
    if update_all:
        posts = list(CONTENT_DIR.glob('*.md'))
        print(f"Updating lastmod for all {len(posts)} posts...")
    else:
        modified = get_modified_posts()
        posts = [CONTENT_DIR.parent.parent / f for f in modified if Path(CONTENT_DIR.parent.parent / f).exists()]
        if not posts:
            print("No modified posts found.")
            return
        print(f"Updating lastmod for {len(posts)} modified posts...")
    
    updated = 0
    for post in posts:
        post_path = Path(post)
        if post_path.exists() and update_lastmod(post_path):
            print(f"  Updated: {post_path.name}")
            updated += 1
    
    print(f"\nDone! Updated {updated} posts.")


if __name__ == "__main__":
    main()
