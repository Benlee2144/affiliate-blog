#!/usr/bin/env python3
"""Download Amazon product images for dehumidifier blog post"""

import urllib.request
import os

# Product image IDs from Amazon
# Extract from product pages - these are the main/hero images

products = {
    "midea-cube-pump": {
        "asin": "B091BYVD2W",
        "image_ids": ["71qJ5j4eXOL", "71pJF7eXOL", "81qV8r8OLOL"]
    },
    "frigidaire-pump": {
        "asin": "B07Z5Q7M3N",
        "image_ids": ["71iO5kpXxLL", "71kN5O7pXxL", "81N8O7pXxLL"]
    },
    "homelabs-pump": {
        "asin": "B08MWTPS9T",
        "image_ids": ["71Kz7aqVpOL", "61qV8r8OLOL", "71N8O7pXxLL"]
    }
}

output_dir = "../static/images/products"
os.makedirs(output_dir, exist_ok=True)

def download_image(image_id, filename):
    url = f"https://m.media-amazon.com/images/I/{image_id}._AC_SL1500_.jpg"
    filepath = os.path.join(output_dir, filename)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            if len(data) > 10000:  # Basic size check
                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"Downloaded: {filename} ({len(data)} bytes)")
                return True
            else:
                print(f"Image too small (error page?): {filename}")
                return False
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return False

# Download main images
download_image("71qJ5j4eXOL", "midea-cube-pump-1.jpg")
download_image("71iO5kpXxLL", "frigidaire-pump-1.jpg")
download_image("71Kz7aqVpOL", "homelabs-pump-1.jpg")

print("\nDone!")
