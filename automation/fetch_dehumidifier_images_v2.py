#!/usr/bin/env python3
"""
Fetch Amazon product images for dehumidifier blog post
Uses absolute paths
"""

import urllib.request
import re
import os
import time

# Use absolute path
output_dir = os.path.expanduser("~/Desktop/amazon website/affiliate-blog/static/images/products")
os.makedirs(output_dir, exist_ok=True)

print(f"Output directory: {output_dir}")

products = [
    {"name": "midea-cube-pump", "asin": "B091BYVD2W"},
    {"name": "frigidaire-pump", "asin": "B07Z5Q7M3N"},
    {"name": "homelabs-pump", "asin": "B08MWTPS9T"},
]

def fetch_amazon_images(asin, name):
    """Fetch Amazon product page and extract image IDs"""
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Find image IDs in the page
            pattern = r'"hiRes":"https://m\.media-amazon\.com/images/I/([A-Za-z0-9]+)\.'
            matches = re.findall(pattern, html)
            
            if not matches:
                pattern = r'images/I/([A-Za-z0-9]+)\._'
                matches = re.findall(pattern, html)
            
            if matches:
                unique_ids = list(dict.fromkeys(matches))[:3]
                print(f"Found image IDs for {name}: {unique_ids}")
                return unique_ids
            else:
                print(f"No image IDs found for {name}")
                return []
    except Exception as e:
        print(f"Error fetching page for {name}: {e}")
        return []

def download_image(image_id, filename):
    """Download image from Amazon CDN"""
    url = f"https://m.media-amazon.com/images/I/{image_id}._AC_SL1500_.jpg"
    filepath = os.path.join(output_dir, filename)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            if len(data) > 10000:
                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"  ✓ Downloaded: {filepath} ({len(data)} bytes)")
                return True
            else:
                print(f"  ✗ Image too small: {filename}")
                return False
    except Exception as e:
        print(f"  ✗ Failed: {filename} - {e}")
        return False

# Process each product
for product in products:
    print(f"\nProcessing {product['name']}...")
    image_ids = fetch_amazon_images(product['asin'], product['name'])
    
    for i, img_id in enumerate(image_ids[:2], 1):
        download_image(img_id, f"{product['name']}-{i}.jpg")
    
    time.sleep(2)

print("\nDone!")
