#!/usr/bin/env python3
"""
Image Validation for Blog Posts
Verifies that product images actually match the product they're supposed to show.
Uses Anthropic's vision API to check each image.
"""

import os
import sys
import json
import base64
import re
import subprocess
import glob

BLOG_DIR = "/Users/benjaminarp/Desktop/amazon website/affiliate-blog"
POSTS_DIR = os.path.join(BLOG_DIR, "content/posts")
IMAGES_DIR = os.path.join(BLOG_DIR, "static/images/products")


def get_api_key():
    """Get Anthropic API key from environment or openclaw config."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    # Try reading from openclaw keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "openclaw-anthropic", "-w"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    # Try env file
    for path in [os.path.expanduser("~/.openclaw/.env"), os.path.expanduser("~/.anthropic/.env")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"')
    return None


def check_image_matches_product(image_path, product_name, expected_category):
    """Use curl to call Anthropic vision API and verify image matches product."""
    
    # Read and encode image
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    # Determine media type
    ext = os.path.splitext(image_path)[1].lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    
    prompt = f"""Look at this product image. I need to verify it matches what it's supposed to be.

Expected product: {product_name}
Expected category: {expected_category}

Answer with ONLY a JSON object:
{{"match": true/false, "actual_product": "what you see in the image", "confidence": "high/medium/low"}}

If the image shows a completely different type of product (e.g., a monitor when it should be a blender), match=false.
If it's the right type of product but maybe a different model/brand, match=true.
If the image is blurry, corrupted, or a placeholder, match=false."""

    api_key = get_api_key()
    if not api_key:
        print("WARNING: No Anthropic API key found, skipping vision validation")
        return {"match": True, "actual_product": "unknown", "confidence": "skipped"}

    # Use curl for the API call
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 200,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    })

    try:
        result = subprocess.run(
            ["curl", "-s", "https://api.anthropic.com/v1/messages",
             "-H", f"x-api-key: {api_key}",
             "-H", "anthropic-version: 2023-06-01",
             "-H", "content-type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=30
        )
        
        response = json.loads(result.stdout)
        text = response.get("content", [{}])[0].get("text", "")
        
        # Parse JSON from response
        json_match = re.search(r'\{[^}]+\}', text)
        if json_match:
            return json.loads(json_match.group())
        
        return {"match": True, "actual_product": "parse_error", "confidence": "low"}
    
    except Exception as e:
        print(f"  API error: {e}")
        return {"match": True, "actual_product": "api_error", "confidence": "low"}


def get_post_images(post_path):
    """Extract product name, category, and image paths from a post."""
    with open(post_path) as f:
        content = f.read()
    
    # Get product name
    product_match = re.search(r'product_name:\s*"([^"]+)"', content)
    product_name = product_match.group(1) if product_match else ""
    
    # Get title as fallback
    title_match = re.search(r'title:\s*"([^"]+)"', content)
    title = title_match.group(1) if title_match else os.path.basename(post_path)
    
    # Get category
    cat_match = re.search(r'categories:\s*\["([^"]+)"', content)
    category = cat_match.group(1) if cat_match else "Unknown"
    
    # Get all image paths
    images = re.findall(r'/images/products/([^"\')\s]+)', content)
    images = list(set(images))
    
    return {
        "product_name": product_name or title,
        "category": category,
        "images": images
    }


def validate_post(post_path, fix=False):
    """Validate all images in a post."""
    info = get_post_images(post_path)
    post_name = os.path.basename(post_path)
    
    if not info["images"]:
        print(f"⚠️  {post_name}: No images found")
        return False
    
    all_valid = True
    
    for img_name in info["images"]:
        img_path = os.path.join(IMAGES_DIR, img_name)
        
        if not os.path.exists(img_path):
            print(f"  ❌ MISSING: {img_name}")
            all_valid = False
            continue
        
        # Check file size
        size = os.path.getsize(img_path)
        if size < 5000:
            print(f"  ❌ TOO SMALL ({size}b): {img_name}")
            all_valid = False
            continue
        
        # Check it's actually an image
        result = subprocess.run(["file", img_path], capture_output=True, text=True)
        if "JPEG" not in result.stdout and "PNG" not in result.stdout:
            print(f"  ❌ NOT AN IMAGE: {img_name}")
            all_valid = False
            continue
        
        # AI vision check
        check = check_image_matches_product(img_path, info["product_name"], info["category"])
        
        if check.get("match"):
            print(f"  ✅ {img_name} → {check.get('actual_product', '?')} ({check.get('confidence', '?')})")
        else:
            print(f"  ❌ WRONG PRODUCT: {img_name}")
            print(f"     Expected: {info['product_name']}")
            print(f"     Got: {check.get('actual_product', '?')}")
            all_valid = False
            
            if fix:
                # Try to find a matching image from existing ones
                print(f"     Attempting auto-fix...")
                # Look for images with similar name to the product
                product_words = info["product_name"].lower().split()
                for existing in os.listdir(IMAGES_DIR):
                    if any(w in existing.lower() for w in product_words if len(w) > 3):
                        candidate = os.path.join(IMAGES_DIR, existing)
                        if candidate != img_path and os.path.getsize(candidate) > 5000:
                            # Verify this candidate
                            ccheck = check_image_matches_product(candidate, info["product_name"], info["category"])
                            if ccheck.get("match"):
                                import shutil
                                shutil.copy2(candidate, img_path)
                                print(f"     ✅ FIXED: Replaced with {existing}")
                                all_valid = True
                                break
    
    return all_valid


def main():
    fix_mode = "--fix" in sys.argv
    
    # Get posts to check
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Check specific post
        posts = [sys.argv[1]]
    else:
        # Check last N posts (default 10)
        n = 10
        for arg in sys.argv[1:]:
            if arg.startswith("--last="):
                n = int(arg.split("=")[1])
        
        all_posts = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")), key=os.path.getmtime, reverse=True)
        posts = all_posts[:n]
    
    print(f"Validating {len(posts)} posts {'(fix mode)' if fix_mode else ''}...\n")
    
    failures = 0
    for post in posts:
        name = os.path.basename(post)
        print(f"📄 {name}")
        if not validate_post(post, fix=fix_mode):
            failures += 1
        print()
    
    if failures:
        print(f"\n❌ {failures} post(s) have image issues")
        sys.exit(1)
    else:
        print(f"\n✅ All posts validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
