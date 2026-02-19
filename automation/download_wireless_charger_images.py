#!/usr/bin/env python3
"""Download Amazon product images for wireless chargers blog post using urllib"""

import urllib.request
import os
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

OUTPUT_DIR = os.path.expanduser("~/Desktop/amazon website/affiliate-blog/static/images/products")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
}

# Real image IDs scraped from Amazon product pages
IMAGES = {
    'anker-maggo-qi2-stand-1.jpg': 'https://m.media-amazon.com/images/I/71EiZw7ksfL._AC_SL1500_.jpg',
    'anker-maggo-2in1-stand-1.jpg': 'https://m.media-amazon.com/images/I/61Hr1i2r1jL._AC_SL1500_.jpg',
    'anker-maggo-3in1-foldable-1.jpg': 'https://m.media-amazon.com/images/I/61Y8TJAnHfL._AC_SL1500_.jpg',
    'belkin-boostcharge-pro-2in1-1.jpg': 'https://m.media-amazon.com/images/I/51uMH5DHYNL._AC_SL1500_.jpg',
    'apple-magsafe-charger-usbc-1.jpg': 'https://m.media-amazon.com/images/I/719qgNv-ubL._AC_SL1500_.jpg',
}

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
            if len(data) < 5000:
                print(f"  WARNING: Too small ({len(data)} bytes): {filepath}")
                return False
            with open(filepath, 'wb') as f:
                f.write(data)
            print(f"  OK: {os.path.basename(filepath)} ({len(data)} bytes)")
            return True
    except Exception as e:
        print(f"  FAILED: {url} -> {e}")
        return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename, url in IMAGES.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
            print(f"  SKIP: {filename}")
            continue
        download_image(url, filepath)
        time.sleep(1)

if __name__ == '__main__':
    main()
