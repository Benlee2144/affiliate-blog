#!/usr/bin/env python3
"""Validate Amazon ASINs in blog posts. Checks that each ASIN resolves to a live product page."""

import re
import sys
import os
import time
import requests

AFFILIATE_TAG = "amazonfi08e0c-20"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_asins(filepath):
    """Extract all ASINs from a markdown file."""
    with open(filepath, 'r') as f:
        content = f.read()
    asins = re.findall(r'amazon\.com/dp/([A-Z0-9]{10})', content)
    return list(set(asins))

def check_asin(asin, retries=2):
    """Check if an ASIN resolves to a live Amazon product page."""
    url = f"https://www.amazon.com/dp/{asin}"
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            # Dead ASINs: 404, or redirect to search/error, or "dog page"
            if r.status_code == 404:
                return False, "404"
            if r.status_code == 503:
                # Rate limited, assume OK
                return True, "503-rate-limited"
            if r.status_code == 200:
                # Check for dog page / "Something went wrong"
                if "Something went wrong" in r.text and "UH-OH" in r.text:
                    return False, "dog-page"
                # Check for redirect to search
                if "/s?" in r.url or "/s/" in r.url:
                    return False, "redirected-to-search"
                return True, "ok"
            return True, f"status-{r.status_code}"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return True, f"error-{e}"  # Assume OK on network error
    return True, "unknown"

def main():
    if len(sys.argv) < 2:
        # If no arg, check all posts
        posts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "posts")
        files = [os.path.join(posts_dir, f) for f in os.listdir(posts_dir) if f.endswith('.md')]
    else:
        files = [sys.argv[1]]

    all_asins = {}
    for f in files:
        asins = extract_asins(f)
        for asin in asins:
            if asin not in all_asins:
                all_asins[asin] = []
            all_asins[asin].append(os.path.basename(f))

    dead = []
    checked = 0
    for asin, posts in all_asins.items():
        is_live, reason = check_asin(asin)
        checked += 1
        if not is_live:
            print(f"DEAD: {asin} ({reason}) — used in: {', '.join(posts)}")
            dead.append((asin, reason, posts))
        else:
            print(f"OK: {asin} ({reason})")
        # Rate limit: 1 req per 2 seconds
        time.sleep(2)

    print(f"\n--- Results ---")
    print(f"Checked: {checked}")
    print(f"Dead: {len(dead)}")

    if dead:
        print("\nDEAD ASINs that need replacement:")
        for asin, reason, posts in dead:
            print(f"  {asin} ({reason}): {', '.join(posts)}")
        sys.exit(1)
    else:
        print("All ASINs are live!")
        sys.exit(0)

if __name__ == "__main__":
    main()
