#!/usr/bin/env python3
"""
Product Validation Script for Affiliate Blog
Validates ASINs and downloads verified product images
"""
import sys
import os
import re
import ssl
import json
import time
import urllib.request
from pathlib import Path

ssl._create_default_https_context = ssl._create_unverified_context

# Verified working ASINs cache (known good products)
# Add products here as they're confirmed working
VERIFIED_ASINS = {
    # Air Fryers
    "B089TQWJKK": "Ninja DZ201 Foodi 8 Quart DualZone Air Fryer",
    "B0936FGLQS": "COSORI Air Fryer Pro 5QT",
    "B07VHFMZHJ": "Instant Pot 6QT Vortex Plus Air Fryer",
    # Blenders
    "B08QCQ8NPL": "Ninja BL770 Mega Kitchen System",
    # Coffee
    "B07P9P9Q9X": "Nespresso Vertuo Next",
    # Electronics - add as discovered
}

def validate_asin(asin):
    """Check if an ASIN is valid on Amazon"""
    # First check our verified cache
    if asin in VERIFIED_ASINS:
        return True, VERIFIED_ASINS[asin]
    
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Check for 404/not found indicators
            if 'Page Not Found' in html or 'Sorry! We couldn' in html:
                return False, "Product not found on Amazon"
            
            # Check for dog page (Amazon's error page)
            if 'Sorry, we just need to make sure' in html:
                return None, "Amazon CAPTCHA - try again later"
            
            # Try to extract product title
            title_match = re.search(r'<span id="productTitle"[^>]*>([^<]+)</span>', html)
            if title_match:
                title = title_match.group(1).strip()
                return True, title
            
            # Alternative title location
            title_match = re.search(r'"title":"([^"]+)"', html)
            if title_match:
                return True, title_match.group(1)
            
            return True, "Product found (title not extracted)"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "ASIN not found (404)"
        return False, f"HTTP Error: {e.code}"
    except Exception as e:
        return None, f"Error: {str(e)}"


def get_amazon_images(asin):
    """Get image IDs from Amazon product page"""
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
        'Accept': 'text/html',
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Find hi-res images
        pattern = r'"hiRes":"https://m\.media-amazon\.com/images/I/([^"]+)"'
        matches = list(set(re.findall(pattern, html)))
        
        # Also try large images
        pattern2 = r'"large":"https://m\.media-amazon\.com/images/I/([^"]+)"'
        matches2 = list(set(re.findall(pattern2, html)))
        
        # Clean up IDs (remove extension variants)
        all_ids = list(set([m.split('.')[0] for m in matches + matches2]))
        return all_ids[:5]
    except:
        return []


def download_image(image_id, output_path):
    """Download high-res image from Amazon CDN"""
    url = f"https://m.media-amazon.com/images/I/{image_id}._AC_SL1500_.jpg"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            
            # Validate it's actually an image
            if len(data) < 10000:
                return False, "Image too small (probably error page)"
            
            # Check JPEG magic bytes
            if not (data[:2] == b'\xff\xd8' or data[:8] == b'\x89PNG\r\n\x1a\n'):
                return False, "Not a valid image file"
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return True, f"Downloaded {len(data):,} bytes"
    except Exception as e:
        return False, str(e)


def download_product_images(asin, prefix, output_dir, count=3):
    """Download images for a product ASIN"""
    results = []
    
    print(f"Getting images for ASIN: {asin}")
    image_ids = get_amazon_images(asin)
    
    if not image_ids:
        print(f"  ❌ No images found")
        return []
    
    print(f"  Found {len(image_ids)} image IDs")
    
    for i, img_id in enumerate(image_ids[:count], 1):
        output_path = os.path.join(output_dir, f"{prefix}-{i}.jpg")
        success, msg = download_image(img_id, output_path)
        
        if success:
            print(f"  ✅ {prefix}-{i}.jpg: {msg}")
            results.append(output_path)
        else:
            print(f"  ❌ {prefix}-{i}.jpg: {msg}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  validate-product.py check <ASIN>           - Validate an ASIN")
        print("  validate-product.py images <ASIN> <prefix> <output_dir> - Download images")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check" and len(sys.argv) >= 3:
        asin = sys.argv[2].upper()
        print(f"Validating ASIN: {asin}")
        
        valid, message = validate_asin(asin)
        
        if valid is True:
            print(f"✅ VALID: {message}")
            sys.exit(0)
        elif valid is False:
            print(f"❌ INVALID: {message}")
            sys.exit(1)
        else:
            print(f"⚠️ UNCERTAIN: {message}")
            sys.exit(2)
    
    elif action == "images" and len(sys.argv) >= 5:
        asin = sys.argv[2].upper()
        prefix = sys.argv[3]
        output_dir = sys.argv[4]
        count = int(sys.argv[5]) if len(sys.argv) > 5 else 3
        
        # First validate the ASIN
        valid, message = validate_asin(asin)
        if valid is False:
            print(f"❌ Invalid ASIN {asin}: {message}")
            sys.exit(1)
        
        print(f"Product: {message}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Download images
        results = download_product_images(asin, prefix, output_dir, count)
        
        if results:
            print(f"\n✅ Downloaded {len(results)} images")
            sys.exit(0)
        else:
            print(f"\n❌ No images downloaded")
            sys.exit(1)
    
    else:
        print("Invalid arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
