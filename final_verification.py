#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def extract_frontmatter_fields(content):
    """Extract title and description from frontmatter."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return None, None
    
    frontmatter = match.group(1)
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    
    title = title_match.group(1) if title_match else ""
    desc = desc_match.group(1) if desc_match else ""
    
    return title, desc

def verify_seo_compliance():
    """Verify all posts meet SEO criteria."""
    posts_dir = "/Users/benjaminarp/Desktop/amazon website/affiliate-blog/content/posts"
    post_files = glob.glob(os.path.join(posts_dir, "*.md"))
    
    compliant_posts = 0
    issues_found = []
    
    print("🔍 FINAL SEO VERIFICATION REPORT")
    print("="*80)
    
    for filepath in sorted(post_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title, desc = extract_frontmatter_fields(content)
        filename = Path(filepath).name
        
        # Check compliance
        title_issues = []
        desc_issues = []
        
        if len(title) > 60:
            title_issues.append(f"TOO LONG ({len(title)} chars)")
        if "(2026)" not in title:
            title_issues.append("MISSING YEAR")
        
        if len(desc) < 140:
            desc_issues.append(f"TOO SHORT ({len(desc)} chars)")
        elif len(desc) > 160:
            desc_issues.append(f"TOO LONG ({len(desc)} chars)")
        
        if title_issues or desc_issues:
            issues_found.append({
                'file': filename,
                'title': title,
                'title_len': len(title),
                'title_issues': title_issues,
                'desc': desc,
                'desc_len': len(desc),
                'desc_issues': desc_issues
            })
        else:
            compliant_posts += 1
    
    # Print summary
    print(f"✅ COMPLIANT POSTS: {compliant_posts}/{len(post_files)}")
    print(f"⚠️  POSTS WITH ISSUES: {len(issues_found)}")
    
    if issues_found:
        print("\n🔧 REMAINING ISSUES:")
        print("-" * 80)
        for issue in issues_found[:10]:  # Show first 10
            print(f"\n📝 {issue['file']}")
            if issue['title_issues']:
                print(f"   TITLE ({issue['title_len']}): {', '.join(issue['title_issues'])}")
            if issue['desc_issues']:
                print(f"   DESC ({issue['desc_len']}): {', '.join(issue['desc_issues'])}")
        
        if len(issues_found) > 10:
            print(f"\n... and {len(issues_found) - 10} more posts with issues")
    
    print("\n" + "="*80)
    return compliant_posts, len(issues_found)

if __name__ == "__main__":
    compliant, issues = verify_seo_compliance()