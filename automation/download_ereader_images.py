#!/usr/bin/env python3
"""Download Amazon product images for e-readers blog post using urllib"""

import urllib.request
import os
import ssl
import time
import re

# Disable SSL verification for simplicity
ssl._create_default_https_context = ssl._create_unverified_context

# Output directory
OUTPUT_DIR = os.path.expanduser("~/Desktop/amazon website/affiliate-blog/static/images/products")

# Headers to mimic browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Products to download images for
PRODUCTS = {
    'kindle-paperwhite-2024': 'B0CFPJYX7P',
    'kobo-libra-colour': 'B0CZXX465Z',
    'kobo-clara-bw': 'B0D1KV8J76',
    'kindle-basic-2024': 'B0CNV9F72P',
}

def get_amazon_images(asin, max_images=3):
    """Fetch hiRes image URLs from Amazon product page"""
    url = f'https://www.amazon.com/dp/{asin}'
    req = urllib.request.Request(url, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Find hiRes images
            hires = re.findall(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
            # Get unique images, take first max_images
            unique = list(dict.fromkeys(hires))[:max_images]
            return unique
    except Exception as e:
        print(f"  Error fetching page for {asin}: {e}")
        return []

def download_image(url, output_path):
    """Download image from URL to output path using urllib"""
    try:
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"  ✓ Downloaded: {os.path.basename(output_path)} ({len(data)} bytes)")
            return True
    except Exception as e:
        print(f"  ✗ Failed to download {os.path.basename(output_path)}: {e}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_success = 0
    total_failed = 0
    
    for product_name, asin in PRODUCTS.items():
        print(f"\n{product_name} ({asin}):")
        
        # Get image URLs from Amazon
        image_urls = get_amazon_images(asin, max_images=3)
        
        if not image_urls:
            print(f"  No images found!")
            total_failed += 3
            continue
        
        # Download each image
        for i, url in enumerate(image_urls, 1):
            filename = f"{product_name}-{i}.jpg"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            if download_image(url, output_path):
                total_success += 1
            else:
                total_failed += 1
            
            time.sleep(0.3)  # Small delay between requests
    
    print(f"\n{'='*50}")
    print(f"Done! Downloaded {total_success} images. Failed: {total_failed}")
    return total_failed == 0

if __name__ == "__main__":
    exit(0 if main() else 1)
