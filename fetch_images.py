#!/usr/bin/env python3
"""Fetch Amazon product images for air purifier blog post."""

import urllib.request
import os
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

output_dir = "static/images/products"

def get_amazon_images(asin):
    """Fetch image IDs from Amazon product page."""
    url = f"https://www.amazon.com/dp/{asin}"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Look for image IDs in various patterns
        patterns = [
            r'"large":"https://m\.media-amazon\.com/images/I/([A-Za-z0-9+_-]+)\._',
            r'"hiRes":"https://m\.media-amazon\.com/images/I/([A-Za-z0-9+_-]+)\._',
            r'data-old-hires="https://m\.media-amazon\.com/images/I/([A-Za-z0-9+_-]+)\._',
            r'https://m\.media-amazon\.com/images/I/([A-Za-z0-9+_-]{10,})\._AC_SL',
        ]
        
        image_ids = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                if m not in image_ids and len(m) > 8:
                    image_ids.append(m)
        
        return image_ids[:5]  # Max 5 images
    except Exception as e:
        print(f"Error fetching {asin}: {e}")
        return []

def download_image(image_id, product_name, index):
    """Download an image from Amazon CDN."""
    url = f"https://m.media-amazon.com/images/I/{image_id}._AC_SL1500_.jpg"
    filename = f"{product_name}-{index}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            if len(data) > 5000:  # Ensure we got a real image
                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"✓ Downloaded: {filename} ({len(data)} bytes)")
                return True
            else:
                print(f"✗ Too small: {filename}")
                return False
    except Exception as e:
        print(f"✗ Failed: {filename} - {e}")
        return False

def main():
    os.makedirs(output_dir, exist_ok=True)
    
    products = {
        "coway-ap1512hh": "B01728NLRG",
        "honeywell-hpa300": "B00BWYO53G",
        "levoit-core-300": "B07VVK39F7",
    }
    
    for product_name, asin in products.items():
        print(f"\n=== Fetching images for {product_name} (ASIN: {asin}) ===")
        image_ids = get_amazon_images(asin)
        print(f"Found {len(image_ids)} image IDs: {image_ids}")
        
        for i, image_id in enumerate(image_ids[:3], 1):  # Download up to 3
            download_image(image_id, product_name, i)

if __name__ == "__main__":
    main()
