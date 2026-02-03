#!/usr/bin/env python3
"""
Amazon Affiliate Blog Post Generator

This script takes an Amazon affiliate link and generates a complete,
SEO-optimized blog post for Hugo. It fetches product images directly
from Amazon and downloads them locally.

Usage:
    python generate_post.py "https://www.amazon.com/dp/B08N5WRWNW?tag=amazonfi08e0c-20"

Requirements:
    pip install requests beautifulsoup4 python-slugify
"""

import argparse
import json
import os
import re
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urljoin
from typing import Optional, Dict, List, Any

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


# ============================================================================
# IMAGE VALIDATION
# ============================================================================

MIN_IMAGE_WIDTH = 200  # Minimum width to consider image valid
MIN_IMAGE_HEIGHT = 200  # Minimum height to consider image valid
MIN_IMAGE_SIZE_KB = 2  # Minimum file size in KB (very small threshold to catch obvious errors)
MAX_IMAGE_WIDTH = 1200  # Max width for web optimization
JPEG_QUALITY = 85  # Quality for JPEG compression (85 is good balance)
MIN_IMAGES_REQUIRED = 3  # Minimum images per blog post (Wirecutter standard)


def validate_image(image_data: bytes) -> tuple[bool, str, tuple[int, int]]:
    """
    Validate that image data is a valid, usable product image.

    Returns:
        (is_valid, reason, dimensions)
    """
    # Check minimum file size
    size_kb = len(image_data) / 1024
    if size_kb < MIN_IMAGE_SIZE_KB:
        return False, f"Image too small ({size_kb:.1f}KB)", (0, 0)

    try:
        # Try to open as image
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size

        # Check dimensions
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            return False, f"Dimensions too small ({width}x{height})", (width, height)

        # Check if it's actually an image format we want
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            return False, f"Unsupported format: {img.format}", (width, height)

        # Check if mostly transparent (placeholder image)
        if img.mode == 'RGBA':
            # Count non-transparent pixels
            alpha = img.split()[-1]
            non_transparent = sum(1 for p in alpha.getdata() if p > 128)
            total = width * height
            if non_transparent / total < 0.1:  # Less than 10% visible
                return False, "Image appears to be mostly transparent", (width, height)

        return True, "Valid", (width, height)

    except Exception as e:
        return False, f"Cannot parse image: {str(e)}", (0, 0)


def optimize_image(image_data: bytes) -> bytes:
    """
    Optimize image for web: resize if too large, compress JPEG.
    Returns optimized image bytes.
    """
    try:
        img = Image.open(io.BytesIO(image_data))

        # Convert to RGB if needed (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if too large (maintain aspect ratio)
        width, height = img.size
        if width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / width
            new_height = int(height * ratio)
            img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
            print(f"  Resized: {width}x{height} -> {MAX_IMAGE_WIDTH}x{new_height}")

        # Save as optimized JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
        optimized = output.getvalue()

        # Report compression
        original_kb = len(image_data) / 1024
        optimized_kb = len(optimized) / 1024
        if optimized_kb < original_kb:
            print(f"  Compressed: {original_kb:.1f}KB -> {optimized_kb:.1f}KB ({100 - (optimized_kb/original_kb*100):.0f}% smaller)")

        return optimized
    except Exception as e:
        print(f"  Optimization failed: {e}, using original")
        return image_data


# ============================================================================
# INTERNAL LINKING HELPER
# ============================================================================

def find_related_posts(category: str, brand: str, exclude_slug: str = "") -> List[Dict[str, str]]:
    """
    Find existing posts that could be linked to from the new post.
    Returns list of {title, url, category} for related posts.
    """
    related = []
    posts_dir = Path(__file__).parent.parent / "content" / "posts"

    if not posts_dir.exists():
        return related

    for post_file in posts_dir.glob("*.md"):
        if post_file.stem == exclude_slug:
            continue

        try:
            content = post_file.read_text(encoding='utf-8')
            # Parse front matter
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    front_matter = content[3:end]
                    post_data = {}
                    for line in front_matter.split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            post_data[key.strip()] = val.strip().strip('"').strip("'")

                    post_title = post_data.get('title', '')
                    post_category = post_data.get('categories', '').strip('[]"')
                    post_brand = post_data.get('brand', '')

                    # Check if related (same category or brand)
                    is_related = False
                    if category and category.lower() in post_category.lower():
                        is_related = True
                    if brand and brand.lower() in post_brand.lower():
                        is_related = True

                    if is_related and post_title:
                        # Generate URL from slug
                        slug = post_file.stem
                        related.append({
                            'title': post_title,
                            'url': f'/{slug}/',
                            'category': post_category,
                            'brand': post_brand,
                        })
        except Exception:
            continue

    return related[:5]  # Return max 5 related posts


# ============================================================================
# CONFIGURATION
# ============================================================================

# Project paths (adjust these if needed)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONTENT_DIR = PROJECT_ROOT / "content" / "posts"
IMAGES_DIR = PROJECT_ROOT / "static" / "images" / "products"

# Multiple user agents for rotation (helps avoid bot detection)
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
]

import random

def get_headers():
    """Get request headers with a random user agent."""
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


# ============================================================================
# BANNED PHRASES - AI SLOP DETECTOR
# ============================================================================

BANNED_PHRASES = [
    "in today's world",
    "whether you're a",
    "in this comprehensive guide",
    "let's dive in",
    "let's explore",
    "look no further",
    "game-changer",
    "game changer",
    "take it to the next level",
    "next level",
    "unlock",
    "unleash",
    "elevate your",
    "navigate the world of",
    "it's important to note",
    "when it comes to",
    "at the end of the day",
    "wondering if",
    "you're not alone",
    "the good news is",
    "here's the deal",
    "the bottom line",
    "rest assured",
    "seamless",
    "seamlessly",
    "robust",
    "straightforward",
    "i'll be honest",
    "without further ado",
    "in conclusion",
    "to summarize",
    "in summary",
    "as we've seen",
    "as you can see",
    "it goes without saying",
    "needless to say",
    "comprehensive",
    "revolutionize",
    "cutting-edge",
    "state-of-the-art",
    "top-notch",
    "world-class",
    "best-in-class",
    "unparalleled",
    "unmatched",
    "second to none",
    "bang for your buck",
    "no-brainer",
    "a must-have",
]

# Phrases that shouldn't start paragraphs
BANNED_PARAGRAPH_STARTS = [
    "so,",
    "now,",
    "well,",
    "look,",
    "listen,",
    "honestly,",
    "basically,",
    "essentially,",
    "fundamentally,",
]


# ============================================================================
# AMAZON PRODUCT FETCHER
# ============================================================================

class AmazonProductFetcher:
    """Fetches product information and images from Amazon."""

    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update(get_headers())
        self.asin = self._extract_asin(url)
        self.affiliate_tag = self._extract_affiliate_tag(url)
        self.product_data: Dict[str, Any] = {}

    def _extract_asin(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL."""
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'ASIN=([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:/|\?|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def _extract_affiliate_tag(self, url: str) -> Optional[str]:
        """Extract affiliate tag from URL."""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('tag', [None])[0]

    def fetch_product_page(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the Amazon product page."""
        if not self.asin:
            print("Error: Could not extract ASIN from URL")
            return None

        # Try different URL formats
        urls_to_try = [
            f"https://www.amazon.com/dp/{self.asin}",
            f"https://www.amazon.com/gp/product/{self.asin}",
        ]

        for url in urls_to_try:
            # Try up to 3 times with different user agents
            for attempt in range(3):
                try:
                    # Rotate user agent on each attempt
                    self.session.headers.update(get_headers())
                    print(f"Fetching: {url} (attempt {attempt + 1})")
                    response = self.session.get(url, timeout=15)

                    if response.status_code == 200:
                        # Check if we got a valid product page
                        soup = BeautifulSoup(response.text, 'html.parser')
                        if soup.select_one("#productTitle, #title, #dp"):
                            return soup
                        print("  Got response but no product content, retrying...")

                    elif response.status_code == 503:
                        print(f"  Rate limited (503), waiting...")
                        time.sleep(5 + attempt * 2)
                    else:
                        print(f"  Status code: {response.status_code}")

                    time.sleep(2 + attempt)  # Increasing delay

                except requests.RequestException as e:
                    print(f"  Request failed: {e}")
                    time.sleep(2)
                    continue

        return None

    def parse_product_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse product information from the page."""
        data = {
            "asin": self.asin,
            "url": self.url,
            "affiliate_tag": self.affiliate_tag,
            "title": "",
            "brand": "",
            "price": "",
            "rating": "",
            "review_count": "",
            "description": "",
            "features": [],
            "images": [],
            "category": "",
        }

        # Title
        title_selectors = [
            "#productTitle",
            "#title",
            "h1.product-title-word-break",
            "span.product-title-word-break",
        ]
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                data["title"] = elem.get_text(strip=True)
                break

        # Brand
        brand_selectors = [
            "#bylineInfo",
            "a#bylineInfo",
            ".po-brand .po-break-word",
            "tr.po-brand td.po-break-word",
        ]
        for selector in brand_selectors:
            elem = soup.select_one(selector)
            if elem:
                brand_text = elem.get_text(strip=True)
                # Clean up "Visit the X Store" or "Brand: X"
                brand_text = re.sub(r'^(Visit the |Brand: )', '', brand_text)
                brand_text = re.sub(r' Store$', '', brand_text)
                data["brand"] = brand_text
                break

        # Price
        price_selectors = [
            ".a-price .a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            ".a-price-whole",
            "#corePrice_feature_div .a-offscreen",
        ]
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price_text = elem.get_text(strip=True)
                if price_text and "$" in price_text:
                    data["price"] = price_text
                    break

        # Rating
        rating_elem = soup.select_one("#acrPopover, .a-icon-star span, [data-hook='rating-out-of-text']")
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                data["rating"] = rating_match.group(1)

        # Review count
        review_elem = soup.select_one("#acrCustomerReviewText, [data-hook='total-review-count']")
        if review_elem:
            review_text = review_elem.get_text(strip=True)
            review_match = re.search(r'([\d,]+)', review_text)
            if review_match:
                data["review_count"] = review_match.group(1).replace(",", "")

        # Features (bullet points)
        feature_list = soup.select("#feature-bullets ul li span.a-list-item")
        if feature_list:
            data["features"] = [
                f.get_text(strip=True)
                for f in feature_list
                if f.get_text(strip=True) and not f.get_text(strip=True).startswith("›")
            ][:8]  # Limit to 8 features

        # Product description
        desc_elem = soup.select_one("#productDescription p, #productDescription")
        if desc_elem:
            data["description"] = desc_elem.get_text(strip=True)[:500]

        # Category/breadcrumb
        breadcrumb = soup.select("#wayfinding-breadcrumbs_feature_div a")
        if breadcrumb:
            categories = [b.get_text(strip=True) for b in breadcrumb]
            data["category"] = categories[-1] if categories else ""

        # Images - multiple sources
        data["images"] = self._extract_images(soup)

        self.product_data = data
        return data

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract all product images from the page using multiple methods."""
        images = []
        seen_urls = set()

        def add_image(url: str) -> bool:
            """Add image if valid and not seen."""
            if not url or url in seen_urls:
                return False
            if "sprite" in url.lower() or "icon" in url.lower() or "transparent" in url.lower():
                return False
            if not url.startswith("http"):
                return False
            # Convert to high-res
            high_res = self._convert_to_high_res(url)
            if high_res not in seen_urls:
                images.append(high_res)
                seen_urls.add(high_res)
                seen_urls.add(url)  # Also mark original
                return True
            return False

        # Method 1: Parse JavaScript data for high-res images (most reliable)
        scripts = soup.find_all("script")
        for script in scripts:
            script_text = script.string or ""

            # Look for colorImages data structure
            if "colorImages" in script_text or "ImageBlockATF" in script_text:
                # Extract hiRes URLs
                hires_matches = re.findall(r'"hiRes"\s*:\s*"([^"]+)"', script_text)
                for url in hires_matches:
                    if add_image(url) and len(images) >= 5:
                        break

                # Extract large URLs as fallback
                large_matches = re.findall(r'"large"\s*:\s*"([^"]+)"', script_text)
                for url in large_matches:
                    if add_image(url) and len(images) >= 5:
                        break

            # Look for imageGalleryData
            if "imageGalleryData" in script_text:
                url_matches = re.findall(r'"mainUrl"\s*:\s*"([^"]+)"', script_text)
                for url in url_matches:
                    if add_image(url) and len(images) >= 5:
                        break

            if len(images) >= 5:
                break

        # Method 2: Main product image element
        main_selectors = [
            "#landingImage",
            "#imgBlkFront",
            "#main-image",
            "#ebooksImgBlkFront",
            "img.a-dynamic-image",
            "#imageBlock img",
        ]
        for selector in main_selectors:
            main_image = soup.select_one(selector)
            if main_image:
                # Try data attributes first (highest res)
                for attr in ["data-old-hires", "data-a-dynamic-image", "data-zoom-hires"]:
                    img_url = main_image.get(attr)
                    if img_url:
                        if img_url.startswith("{"):
                            try:
                                img_data = json.loads(img_url)
                                # Get the largest image from JSON
                                img_url = max(img_data.keys(), key=lambda x: img_data[x][0] * img_data[x][1])
                            except:
                                continue
                        add_image(img_url)

                # Fallback to src
                src = main_image.get("src")
                if src:
                    add_image(src)

            if len(images) >= 5:
                break

        # Method 3: Thumbnail strip images
        thumb_selectors = [
            "#altImages img",
            ".imageThumbnail img",
            "#imageBlock_feature_div img",
            ".image-thumbnail img",
            "li.image img",
        ]
        for selector in thumb_selectors:
            thumbnails = soup.select(selector)
            for thumb in thumbnails:
                src = thumb.get("src", "")
                if add_image(src) and len(images) >= 5:
                    break
            if len(images) >= 5:
                break

        # Method 4: Construct image URL from ASIN (fallback)
        if not images and self.asin:
            # Amazon image URL pattern
            base_url = f"https://m.media-amazon.com/images/I/{self.asin}._SL1500_.jpg"
            images.append(base_url)
            print(f"  Using constructed image URL: {base_url}")

        return images[:5]  # Return max 5 images

    def _convert_to_high_res(self, url: str) -> str:
        """Convert Amazon image URL to high-resolution version."""
        # Amazon image URLs often contain size indicators like _SS40_, _SX300_, etc.
        # Replace with larger size
        patterns = [
            (r'\._[A-Z]{2}\d+_\.', '._SL1500_.'),
            (r'\._[A-Z]{2}\d+,\d+_\.', '._SL1500_.'),
            (r'\._S[XY]\d+_\.', '._SL1500_.'),
        ]
        result = url
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result

    def download_images(self, product_slug: str) -> List[Dict[str, str]]:
        """Download product images to local storage with validation."""
        downloaded = []
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        valid_image_num = 0

        for i, img_url in enumerate(self.product_data.get("images", [])):
            try:
                print(f"Downloading image {i + 1}: {img_url[:80]}...")
                response = self.session.get(img_url, timeout=15)
                if response.status_code == 200:
                    image_data = response.content

                    # Validate the image before saving
                    is_valid, reason, dimensions = validate_image(image_data)
                    if not is_valid:
                        print(f"  Skipped (invalid): {reason}")
                        continue

                    valid_image_num += 1
                    width, height = dimensions
                    print(f"  Valid image: {width}x{height}")

                    # Optimize image for web (resize, compress, convert to JPEG)
                    image_data = optimize_image(image_data)
                    ext = ".jpg"  # Always save as JPEG after optimization

                    # Generate filename
                    filename = f"{product_slug}-{valid_image_num}{ext}"
                    filepath = IMAGES_DIR / filename

                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(image_data)

                    downloaded.append({
                        "local_path": f"/affiliate-blog/images/products/{filename}",
                        "filename": filename,
                        "alt": f"{self.product_data.get('title', 'Product')} - Image {valid_image_num}",
                        "original_url": img_url,
                        "dimensions": f"{width}x{height}",
                    })
                    print(f"  Saved: {filename} ({width}x{height})")
                    time.sleep(0.5)  # Rate limiting

                    # Stop after 5 valid images
                    if valid_image_num >= 5:
                        break

            except Exception as e:
                print(f"  Failed to download image: {e}")

        # If no valid images found, try fallback methods
        if not downloaded:
            print("  No valid images found, trying fallback...")
            downloaded = self._download_fallback_images(product_slug)

        return downloaded

    def _download_fallback_images(self, product_slug: str) -> List[Dict[str, str]]:
        """Try alternative methods to get product images."""
        downloaded = []

        if not self.asin:
            return downloaded

        # Try different Amazon image URL patterns
        fallback_patterns = [
            f"https://m.media-amazon.com/images/I/{self.asin}._AC_SL1500_.jpg",
            f"https://m.media-amazon.com/images/I/{self.asin}._SL1500_.jpg",
            f"https://images-na.ssl-images-amazon.com/images/I/{self.asin}._AC_SL1500_.jpg",
        ]

        for pattern_url in fallback_patterns:
            try:
                print(f"  Trying fallback: {pattern_url[:60]}...")
                response = self.session.get(pattern_url, timeout=10)
                if response.status_code == 200:
                    is_valid, reason, dimensions = validate_image(response.content)
                    if is_valid:
                        filename = f"{product_slug}-1.jpg"
                        filepath = IMAGES_DIR / filename
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        downloaded.append({
                            "local_path": f"/affiliate-blog/images/products/{filename}",
                            "filename": filename,
                            "alt": f"{self.product_data.get('title', 'Product')} - Main Image",
                            "original_url": pattern_url,
                            "dimensions": f"{dimensions[0]}x{dimensions[1]}",
                        })
                        print(f"  Fallback successful: {filename}")
                        break
            except Exception as e:
                continue

        return downloaded


# ============================================================================
# CONTENT GENERATOR
# ============================================================================

class BlogPostGenerator:
    """
    Generates Wirecutter-style blog post content.

    Key principles (from WIRECUTTER_STYLE_GUIDE.md):
    - Reader service first
    - "Good enough" recommendations (value + price intersection)
    - Research depth like recommending to friends/family
    - Balanced honesty (always disclose weaknesses)
    - Quick pick box immediately after intro
    - Specific over vague ("1400-watt motor" not "powerful")
    - Real user feedback cited (Reddit, forums, verified reviews)
    - Clear "who should buy" and "who should skip"
    """

    def __init__(self, product_data: Dict[str, Any], images: List[Dict[str, str]]):
        self.product = product_data
        self.images = images
        self.slug = self._generate_slug()

    def _generate_slug(self) -> str:
        """Generate URL-friendly slug from product title."""
        title = self.product.get("title", "product-review")
        # Remove brand name if at start of title
        brand = self.product.get("brand", "")
        if brand and title.lower().startswith(brand.lower()):
            title = title[len(brand):].strip()

        # Create slug
        slug = slugify(title, max_length=60, word_boundary=True)
        if not slug.endswith("-review"):
            slug += "-review"
        return slug

    def _check_banned_phrases(self, text: str) -> List[str]:
        """Check for banned AI-sounding phrases."""
        found = []
        text_lower = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in text_lower:
                found.append(phrase)
        return found

    def generate_front_matter(self) -> str:
        """
        Generate Hugo front matter with Wirecutter-style metadata:
        - Title format: "Best [Category] for [Use Case]" or "[Product] Review (Tested)"
        - Strong meta description for CTR
        - Schema-ready structured data
        """
        title = self.product.get("title", "Product Review")
        brand = self.product.get("brand", "")
        price = self.product.get("price", "")
        rating = self.product.get("rating", "4")
        category = self.product.get("category", "Reviews")
        year = datetime.now().year

        # Build affiliate link
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")
        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"

        # Main image
        main_image = self.images[0]["local_path"] if self.images else ""

        # Generate keywords
        keywords = self._generate_keywords()

        # Wirecutter-style title (keyword-first with context)
        seo_title = f"{title} Review ({year}): Tested & Researched"

        # Wirecutter-style meta description (compelling, specific)
        meta_desc = f"After analyzing {self.product.get('review_count', 'thousands of')} owner reviews and Reddit discussions, here's whether the {title} is worth buying—plus who should skip it."

        front_matter = f'''---
title: "{seo_title}"
date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}+00:00
lastmod: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}+00:00
draft: false
description: "{meta_desc}"
summary: "Our research-backed verdict on the {title}: who it's perfect for, honest downsides, and how it compares to alternatives."

keywords: [{', '.join(f'"{k}"' for k in keywords)}]

categories: ["{category}"]
tags: ["{brand}", "{category.lower()}", "product review", "buying guide"]

review: true
product_name: "{title}"
product_image: "{main_image}"
brand: "{brand}"
rating: {rating if rating else 4}
price: "{price}"
affiliate_link: "{affiliate_link}"
asin: "{asin}"

author: "Benjamin Arp"
showToc: true
TocOpen: true

cover:
    image: "{main_image}"
    alt: "{title}"
    caption: "Our top pick after extensive research"
    relative: false
---

**Affiliate Disclosure:** We earn a commission if you make a purchase, at no extra cost to you. We only recommend products we've thoroughly researched. [Learn more](/affiliate-disclosure/)

'''
        return front_matter

    def _generate_keywords(self) -> List[str]:
        """Generate relevant SEO keywords."""
        title = self.product.get("title", "")
        brand = self.product.get("brand", "")
        category = self.product.get("category", "")

        keywords = []

        # Brand + product keywords
        if brand:
            keywords.append(f"{brand} review")
            keywords.append(f"is {brand} good")

        # Product-specific
        keywords.append(f"{title} review")
        keywords.append(f"{title} worth it")
        keywords.append(f"best {category.lower()}")

        # Intent keywords
        keywords.append(f"{title} pros and cons")
        keywords.append(f"{title} vs")

        return keywords[:8]

    def generate_content(self) -> str:
        """Generate the main blog post content."""
        title = self.product.get("title", "Product")
        brand = self.product.get("brand", "")
        price = self.product.get("price", "Check current price")
        features = self.product.get("features", [])
        description = self.product.get("description", "")
        rating = self.product.get("rating", "4.5")
        review_count = self.product.get("review_count", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")

        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"

        # Build content sections
        content_parts = []

        # Hook intro (addresses pain point)
        content_parts.append(self._generate_intro())

        # Main product image with CTA
        if self.images:
            content_parts.append(self._generate_product_box())

        # Quick verdict
        content_parts.append(self._generate_quick_verdict())

        # Features section
        if features:
            content_parts.append(self._generate_features_section())

        # Pros and cons
        content_parts.append(self._generate_pros_cons())

        # Who should buy / skip
        content_parts.append(self._generate_who_should_buy())

        # Competition comparison
        content_parts.append(self._generate_comparison())

        # Gallery of additional images
        if len(self.images) > 1:
            content_parts.append(self._generate_image_gallery())

        # Final verdict
        content_parts.append(self._generate_verdict())

        # Internal links to related posts
        related = self._generate_related_links()
        if related:
            content_parts.append(related)

        # FAQ section
        content_parts.append(self._generate_faq())

        return "\n\n".join(content_parts)

    def _generate_intro(self) -> str:
        """
        Generate Wirecutter-style intro that:
        - Opens with reader's pain point
        - Establishes credibility through research depth
        - Uses bold to emphasize main focus
        - Leads directly into the top pick
        """
        title = self.product.get("title", "this product")
        category = self.product.get("category", "product")
        brand = self.product.get("brand", "")
        review_count = self.product.get("review_count", "")

        # Wirecutter-style opening: pain point + credibility + bold focus
        intro = f"""Finding the right {category.lower() if category else "product"} shouldn't require hours of research through fake reviews and sponsored content. After analyzing {f"{review_count}+ verified owner reviews" if review_count else "hundreds of verified reviews"}, Reddit discussions in r/{category.replace(' ', '').lower() if category else "BuyItForLife"}, and long-term ownership reports, we've identified what actually works—and what leaves buyers frustrated.

**Our top pick is the {title}**, which consistently earns praise from owners who've used it for months, not just days. But depending on your specific needs and budget, we have alternatives worth considering too."""

        return intro

    def _generate_product_box(self) -> str:
        """Generate main product showcase box."""
        title = self.product.get("title", "Product")
        price = self.product.get("price", "")
        rating = self.product.get("rating", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")
        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"
        image = self.images[0] if self.images else None

        box = f"""{{{{< product-box
    name="{title}"
    image="{image['local_path'] if image else ''}"
    price="{price}"
    link="{affiliate_link}"
    rating="{rating}"
>}}}}"""
        return box

    def _generate_quick_verdict(self) -> str:
        """
        Generate Wirecutter-style quick verdict:
        - Appears immediately after intro
        - Single sentence summary of primary selling point
        - Who it's best for
        - Direct, confident recommendation
        """
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        rating = self.product.get("rating", "4")
        price = self.product.get("price", "")
        category = self.product.get("category", "")

        try:
            rating_val = float(rating)
        except:
            rating_val = 4.0

        if rating_val >= 4.5:
            confidence = "confidently recommend"
            verdict = "the best option for most people"
        elif rating_val >= 4.0:
            confidence = "recommend"
            verdict = "a solid choice that delivers on its promises"
        else:
            confidence = "cautiously recommend"
            verdict = "good for specific use cases"

        verdict_section = f"""## Our Pick: {title}

**The quick take:** [RESEARCH: One specific, compelling benefit that real owners highlight—e.g., "The 1400-watt motor pulverizes ice in under 10 seconds" or "Runs so quietly it doesn't wake sleeping babies"]

We {confidence} the **{title}** as {verdict}. At {price if price else "[check current price]"}, it hits the sweet spot between performance and value that most buyers are looking for.

**Best for:** [RESEARCH: Specific user type based on review analysis]

**Skip if:** [RESEARCH: Specific limitation that makes this wrong for some buyers]"""

        return verdict_section

    def _generate_features_section(self) -> str:
        """Generate features section with benefits."""
        features = self.product.get("features", [])
        if not features:
            return ""

        section = """## Key Features (And Why They Actually Matter)

Here's what you're getting:

"""
        for feature in features[:6]:
            # Clean up the feature text
            feature = feature.strip()
            if len(feature) > 20:  # Only include substantial features
                section += f"- **{feature[:50]}{'...' if len(feature) > 50 else ''}** — {feature}\n"

        return section

    def _generate_pros_cons(self) -> str:
        """
        Generate Wirecutter-style pros/cons:
        - Cite specific sources (Reddit, Amazon, YouTube)
        - Use concrete details, not vague praise
        - Include cons honestly—builds trust
        """
        title = self.product.get("title", "this product")
        features = self.product.get("features", [])
        rating = self.product.get("rating", "4")
        brand = self.product.get("brand", "")

        section = f"""## Why the {title} Stands Out

Based on our analysis of long-term owner feedback:

**What owners love after months of use:**

- [RESEARCH: Specific pro with source - e.g., "Multiple Reddit users in r/Blenders praise the quiet operation, with one noting 'I can make smoothies at 6am without waking anyone'"]
- [RESEARCH: Specific pro - quote actual review language when possible]
- [RESEARCH: Specific pro - look for unexpected benefits owners discover]

**The honest downsides:**

Every product has weaknesses. Here's what real owners report:

- [RESEARCH: Specific con - e.g., "Several 3-star Amazon reviews mention the lid is hard to clean if smoothie dries on it"]
- [RESEARCH: Specific con - common complaint pattern]
- [RESEARCH: Limitation or "gotcha" - things the marketing doesn't mention]

**The verdict on durability:** [RESEARCH: What do 6-month and 1-year owners say about how it holds up?]"""

        return section

    def _generate_who_should_buy(self) -> str:
        """
        Generate Wirecutter-style buyer guidance:
        - Super specific about ideal users
        - Equally specific about who should NOT buy
        - Based on actual review patterns
        """
        title = self.product.get("title", "this product")
        category = self.product.get("category", "product")
        price = self.product.get("price", "")
        brand = self.product.get("brand", "")

        section = f"""## Who Should Buy the {title}

**Get this if you:**

- [RESEARCH: Specific use case #1 - e.g., "You make smoothies 3+ times per week and want something that handles frozen fruit without struggling"]
- [RESEARCH: Specific use case #2 - e.g., "You have a small kitchen and need a compact option that still performs"]
- [RESEARCH: Specific user type - e.g., "You value quiet operation over raw power"]
- Want a {category.lower() if category else "product"} that [RESEARCH: key benefit pattern from reviews]

**Skip this if you:**

- [RESEARCH: Specific deal-breaker #1 - e.g., "You need to blend hot liquids—the plastic jar isn't designed for it"]
- [RESEARCH: Specific deal-breaker #2 - e.g., "You want a glass container—this only comes with plastic"]
- [RESEARCH: Alternative recommendation - e.g., "You're on a tight budget—the [Competitor] does 80% of the job for half the price"]
- Need [RESEARCH: specific feature this lacks]"""

        return section

    def _generate_comparison(self) -> str:
        """
        Generate Wirecutter-style comparison:
        - Name specific competitors by model
        - Compare on specs that actually matter
        - Give clear, opinionated guidance
        """
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        price = self.product.get("price", "")
        category = self.product.get("category", "")
        rating = self.product.get("rating", "N/A")

        section = f"""## The Competition: How It Stacks Up

| | **{title[:25]}** | **[RESEARCH: Competitor A]** | **[RESEARCH: Competitor B]** |
|---|---|---|---|
| **Price** | {price if price else "[Check]"} | [RESEARCH] | [RESEARCH] |
| **[Key Spec 1]** | [Value] | [Value] | [Value] |
| **[Key Spec 2]** | [Value] | [Value] | [Value] |
| **[Key Spec 3]** | [Value] | [Value] | [Value] |
| **Amazon Rating** | {rating}/5 | [RESEARCH]/5 | [RESEARCH]/5 |
| **Our Take** | Best overall | [RESEARCH: One-line verdict] | [RESEARCH: One-line verdict] |

### {title} vs [Competitor A]

[RESEARCH: Direct head-to-head comparison. Be opinionated—which is better and why? When would you choose the competitor instead?]

### {title} vs [Competitor B]

[RESEARCH: Same approach. If the competitor is better for certain use cases, say so clearly.]

**Bottom line:** The {title} is our pick for [RESEARCH: specific use case]. If you [RESEARCH: different priority], consider [Competitor] instead."""

        return section

    def _generate_image_gallery(self) -> str:
        """
        Generate gallery of product images.
        Wirecutter uses multiple images throughout articles for visual breaks.
        Minimum 3 images per post.
        """
        if len(self.images) <= 1:
            return """## Product Gallery

[IMAGES NEEDED: Add at least 2 more product images. Download from Amazon listing or product manufacturer site. Save to /static/images/products/]

"""

        gallery = """## Product Gallery

"""
        for i, img in enumerate(self.images[1:], start=2):
            gallery += f"""![{img['alt']}]({img['local_path']})

"""

        if len(self.images) < MIN_IMAGES_REQUIRED:
            gallery += f"""
[NOTE: Only {len(self.images)} images available. Consider adding more for better visual engagement.]

"""
        return gallery

    def _generate_verdict(self) -> str:
        """
        Generate Wirecutter-style final verdict:
        - Restate the recommendation clearly
        - One compelling reason based on research
        - Strong CTA with affiliate link
        """
        title = self.product.get("title", "this product")
        price = self.product.get("price", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")
        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"
        rating = self.product.get("rating", "4")
        brand = self.product.get("brand", "")
        category = self.product.get("category", "")

        try:
            rating_val = float(rating)
        except:
            rating_val = 4.0

        if rating_val >= 4.5:
            confidence = "our top recommendation"
            cta_text = "Check Price on Amazon"
        elif rating_val >= 4.0:
            confidence = "a solid choice we're confident recommending"
            cta_text = "See Current Price"
        else:
            confidence = "worth considering for the right buyer"
            cta_text = "View on Amazon"

        section = f"""## The Bottom Line

The **{title}** is {confidence} for most people shopping in this category.

[RESEARCH: One specific, memorable point that summarizes why—e.g., "When a product maintains a 4.6-star average across 15,000+ reviews with owners specifically praising it after 2+ years of use, that tells you something about real-world reliability."]

At {price if price else "[current price]"}, you're getting [RESEARCH: what the value proposition actually is]. For most buyers, that's the right balance of [RESEARCH: key tradeoffs].

If it matches what you need, you won't be disappointed.

{{{{< cta-button url="{affiliate_link}" text="{cta_text}" >}}}}

*Prices and availability are accurate as of the publication date. We update our recommendations when better options emerge.*"""

        return section

    def _generate_related_links(self) -> str:
        """Generate internal links to related posts for SEO."""
        category = self.product.get("category", "")
        brand = self.product.get("brand", "")

        related_posts = find_related_posts(category, brand, self.slug)

        if not related_posts:
            return ""

        section = """## Related Reviews

If you're still deciding, check out these related reviews:

"""
        for post in related_posts:
            section += f"- [{post['title']}]({post['url']})\n"

        return section

    def _generate_faq(self) -> str:
        """
        Generate Wirecutter-style FAQ:
        - Use actual questions from Google "People Also Ask"
        - Pull from Amazon Q&A section
        - Answer directly, don't hedge
        - Include schema-ready structure
        """
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        category = self.product.get("category", "product")
        price = self.product.get("price", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")

        section = f"""## Frequently Asked Questions

### Is the {title} worth {price if price else "the price"}?

[RESEARCH: Direct answer. Look at what 3-4 star reviewers say about value—they're usually the most balanced. Example: "At $X, most owners feel they got good value. The common sentiment is that it does 90% of what $200+ models do."]

### How long does the {title} last?

[RESEARCH: Find specific durability reports. Example: "Based on reviews from owners who've had it 1-2 years, the motor holds up well but the [specific part] may need replacement after heavy use."]

### What's the warranty?

[RESEARCH: Actual warranty details from the listing. Example: "{brand} offers a 2-year limited warranty covering manufacturing defects. Some owners report good experiences with customer service for issues within warranty."]

### {title} vs [RESEARCH: Top searched competitor]?

[RESEARCH: Clear, opinionated comparison. Don't say "it depends"—say which one is better for what use case.]

### Is it loud?

[RESEARCH: Specific noise level info if relevant to this category. Example: "Multiple reviewers measured it around 65-70 decibels, comparable to normal conversation. Noticeably quieter than [competitor]."]

### Where can I get the best deal?

Amazon typically matches or beats other retailers, and Prime members get free shipping. Prices fluctuate based on demand and sales events:

{{{{< cta-button url="https://www.amazon.com/dp/{asin}?tag={tag}" text="Check Current Price" >}}}}"""

        return section

    def generate_full_post(self) -> str:
        """Generate the complete blog post."""
        front_matter = self.generate_front_matter()
        content = self.generate_content()

        full_post = front_matter + "\n" + content

        # Check for banned phrases
        banned_found = self._check_banned_phrases(full_post)
        if banned_found:
            print(f"\n⚠️  WARNING: Found AI-sounding phrases that should be removed:")
            for phrase in banned_found:
                print(f"   - \"{phrase}\"")

        return full_post

    def save_post(self) -> Path:
        """Save the post to the content directory."""
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)

        filename = f"{self.slug}.md"
        filepath = CONTENT_DIR / filename

        content = self.generate_full_post()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Amazon affiliate blog posts for Hugo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_post.py "https://www.amazon.com/dp/B08N5WRWNW?tag=amazonfi08e0c-20"
  python generate_post.py --no-images "https://amazon.com/dp/B08N5WRWNW"
        """
    )
    parser.add_argument("url", help="Amazon product URL (with or without affiliate tag)")
    parser.add_argument("--no-images", action="store_true", help="Skip downloading images")
    parser.add_argument("--output-dir", type=Path, help="Custom output directory for posts")

    args = parser.parse_args()

    print("=" * 60)
    print("Amazon Affiliate Blog Post Generator")
    print("=" * 60)

    # Fetch product data
    print(f"\n📦 Fetching product from: {args.url}")
    fetcher = AmazonProductFetcher(args.url)

    soup = fetcher.fetch_product_page()
    if not soup:
        print("❌ Failed to fetch product page. Amazon might be blocking requests.")
        print("   Try again in a few minutes or use a VPN.")
        sys.exit(1)

    product_data = fetcher.parse_product_data(soup)

    print(f"\n✅ Found product: {product_data.get('title', 'Unknown')}")
    print(f"   Brand: {product_data.get('brand', 'N/A')}")
    print(f"   Price: {product_data.get('price', 'N/A')}")
    print(f"   Rating: {product_data.get('rating', 'N/A')}/5")
    print(f"   Images found: {len(product_data.get('images', []))}")

    # Download images (minimum 3 required per post)
    images = []
    if not args.no_images and product_data.get("images"):
        print(f"\n📸 Downloading product images (minimum {MIN_IMAGES_REQUIRED} required)...")
        slug = slugify(product_data.get("title", "product"), max_length=40)
        images = fetcher.download_images(slug)
        print(f"   Downloaded {len(images)} images")

        if len(images) < MIN_IMAGES_REQUIRED:
            print(f"\n⚠️  WARNING: Only {len(images)} images found. Posts should have at least {MIN_IMAGES_REQUIRED} images.")
            print(f"   Consider manually adding more product images to: {IMAGES_DIR}")

    # Generate blog post
    print(f"\n📝 Generating blog post...")
    generator = BlogPostGenerator(product_data, images)
    filepath = generator.save_post()

    print(f"\n✅ Blog post created: {filepath}")
    print(f"\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Open the generated post and replace [RESEARCH] placeholders
   with actual findings from:
   - Reddit discussions
   - YouTube reviews
   - Amazon verified purchase reviews
   - Forum threads

2. Run: hugo server -D
   To preview locally at http://localhost:1313

3. When ready, remove 'draft: true' from front matter

4. Commit and push to deploy to GitHub Pages
""")

    if images:
        print("📸 Images saved to:")
        for img in images:
            print(f"   {img['local_path']}")


if __name__ == "__main__":
    main()
