#!/usr/bin/env python3
"""
Fetch Amazon product data and images only.
Claude will write the actual blog content.

Usage:
    python fetch_product.py "https://www.amazon.com/dp/XXXXX?tag=your-tag"
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import random

try:
    import requests
    from bs4 import BeautifulSoup
    from slugify import slugify
    from PIL import Image
    import io
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install requests beautifulsoup4 python-slugify pillow")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
IMAGES_DIR = PROJECT_ROOT / "static" / "images" / "products"

# Image settings
MIN_IMAGE_SIZE = 200
MAX_IMAGE_WIDTH = 1200
JPEG_QUALITY = 85

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def extract_asin(url):
    patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/product/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None


def extract_tag(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('tag', ['amazonfi08e0c-20'])[0]


def fetch_product(url):
    """Fetch product data from Amazon."""
    asin = extract_asin(url)
    tag = extract_tag(url)
    
    if not asin:
        return None
    
    session = requests.Session()
    session.headers.update(get_headers())
    
    for attempt in range(3):
        try:
            response = session.get(f"https://www.amazon.com/dp/{asin}", timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract data
                data = {
                    "asin": asin,
                    "affiliate_tag": tag,
                    "affiliate_link": f"https://www.amazon.com/dp/{asin}?tag={tag}",
                }
                
                # Title
                title_elem = soup.select_one("#productTitle, #title")
                data["title"] = title_elem.get_text(strip=True) if title_elem else ""
                
                # Brand
                brand_elem = soup.select_one("#bylineInfo, .po-brand .po-break-word")
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
                    brand = re.sub(r'^(Visit the |Brand: )', '', brand)
                    brand = re.sub(r' Store$', '', brand)
                    data["brand"] = brand
                else:
                    data["brand"] = ""
                
                # Price
                price_elem = soup.select_one(".a-price .a-offscreen, #priceblock_ourprice")
                data["price"] = price_elem.get_text(strip=True) if price_elem else ""
                
                # Rating
                rating_elem = soup.select_one("#acrPopover, [data-hook='rating-out-of-text']")
                if rating_elem:
                    match = re.search(r'(\d+\.?\d*)', rating_elem.get_text())
                    data["rating"] = match.group(1) if match else "4.5"
                else:
                    data["rating"] = "4.5"
                
                # Review count
                review_elem = soup.select_one("#acrCustomerReviewText")
                if review_elem:
                    match = re.search(r'([\d,]+)', review_elem.get_text())
                    data["review_count"] = match.group(1).replace(",", "") if match else ""
                else:
                    data["review_count"] = ""
                
                # Features
                features = []
                for feat in soup.select("#feature-bullets li span.a-list-item"):
                    text = feat.get_text(strip=True)
                    if text and not text.startswith("›") and len(text) > 10:
                        features.append(text)
                data["features"] = features[:8]
                
                # Category
                breadcrumbs = soup.select("#wayfinding-breadcrumbs_feature_div a")
                data["category"] = breadcrumbs[-1].get_text(strip=True) if breadcrumbs else "Reviews"
                
                # Images
                images = []
                for script in soup.find_all("script"):
                    text = script.string or ""
                    if "colorImages" in text or "ImageBlockATF" in text:
                        for match in re.findall(r'"hiRes"\s*:\s*"([^"]+)"', text):
                            if match not in images:
                                images.append(match)
                        for match in re.findall(r'"large"\s*:\s*"([^"]+)"', text):
                            if match not in images:
                                images.append(match)
                data["images"] = images[:5]
                
                return data
                
            time.sleep(2)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    
    return None


def optimize_image(image_data):
    """Optimize image for web."""
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed
        width, height = img.size
        if width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / width
            img = img.resize((MAX_IMAGE_WIDTH, int(height * ratio)), Image.LANCZOS)
        
        # Save as JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        return output.getvalue(), img.size
    except:
        return image_data, (0, 0)


def download_images(product_data, slug):
    """Download and optimize product images."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []
    session = requests.Session()
    session.headers.update(get_headers())
    
    for i, url in enumerate(product_data.get("images", [])):
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data, size = optimize_image(response.content)
                if size[0] >= MIN_IMAGE_SIZE and size[1] >= MIN_IMAGE_SIZE:
                    filename = f"{slug}-{i + 1}.jpg"
                    filepath = IMAGES_DIR / filename
                    with open(filepath, "wb") as f:
                        f.write(data)
                    downloaded.append({
                        "path": f"/images/products/{filename}",
                        "filename": filename,
                        "size": f"{size[0]}x{size[1]}"
                    })
                    print(f"  Saved: {filename} ({size[0]}x{size[1]})")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Failed: {e}")
    
    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Fetch Amazon product data")
    parser.add_argument("url", help="Amazon product URL")
    args = parser.parse_args()
    
    print("Fetching product data...")
    product = fetch_product(args.url)
    
    if not product:
        print("Failed to fetch product")
        sys.exit(1)
    
    print(f"\nProduct: {product['title']}")
    print(f"Brand: {product['brand']}")
    print(f"Price: {product['price']}")
    print(f"Rating: {product['rating']}/5 ({product['review_count']} reviews)")
    print(f"ASIN: {product['asin']}")
    
    # Download images
    slug = slugify(product['title'], max_length=40)
    print(f"\nDownloading images...")
    images = download_images(product, slug)
    product["downloaded_images"] = images
    product["slug"] = slug
    
    # Save to JSON for Claude to use
    output_file = SCRIPT_DIR / "last_product.json"
    with open(output_file, "w") as f:
        json.dump(product, f, indent=2)
    
    print(f"\nProduct data saved to: {output_file}")
    print(f"Images saved: {len(images)}")
    
    return product


if __name__ == "__main__":
    main()
