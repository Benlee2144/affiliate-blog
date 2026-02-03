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

                    # Determine actual format from image data
                    try:
                        img = Image.open(io.BytesIO(image_data))
                        actual_format = img.format.lower() if img.format else 'jpeg'
                        # Convert WebP to JPEG for better compatibility
                        if actual_format == 'webp':
                            # Convert to RGB (remove alpha if present)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                            # Save as JPEG
                            output = io.BytesIO()
                            img.save(output, format='JPEG', quality=90)
                            image_data = output.getvalue()
                            actual_format = 'jpeg'
                            print(f"  Converted WebP to JPEG")
                    except:
                        actual_format = 'jpeg'

                    ext = ".jpg" if actual_format == 'jpeg' else f".{actual_format}"

                    # Generate filename
                    filename = f"{product_slug}-{valid_image_num}{ext}"
                    filepath = IMAGES_DIR / filename

                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(image_data)

                    downloaded.append({
                        "local_path": f"/images/products/{filename}",
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
                            "local_path": f"/images/products/{filename}",
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
    """Generates anti-AI-slop blog post content."""

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
        """Generate Hugo front matter YAML."""
        title = self.product.get("title", "Product Review")
        brand = self.product.get("brand", "")
        price = self.product.get("price", "")
        rating = self.product.get("rating", "4")
        category = self.product.get("category", "Reviews")

        # Build affiliate link
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")
        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"

        # Main image
        main_image = self.images[0]["local_path"] if self.images else ""

        # Generate keywords
        keywords = self._generate_keywords()

        front_matter = f'''---
title: "{title} Review: Is It Worth It in {datetime.now().year}?"
date: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}+00:00
lastmod: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}+00:00
draft: false
description: "Honest {title} review with real user feedback. Find out if this {category.lower()} is worth your money, who it's best for, and what the downsides are."
summary: "A no-BS review of the {title} based on real owner experiences and hands-on research."

keywords: [{', '.join(f'"{k}"' for k in keywords)}]

categories: ["{category}"]
tags: ["{brand} review", "{category.lower()}", "product review", "amazon"]

review: true
product_name: "{title}"
product_image: "{main_image}"
brand: "{brand}"
rating: {rating if rating else 4}
price: "{price}"
affiliate_link: "{affiliate_link}"

cover:
    image: "{main_image}"
    alt: "{title}"
    caption: ""
    relative: false
---
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

        # FAQ section
        content_parts.append(self._generate_faq())

        return "\n\n".join(content_parts)

    def _generate_intro(self) -> str:
        """Generate hook intro that addresses buyer pain point."""
        title = self.product.get("title", "this product")
        category = self.product.get("category", "product")
        brand = self.product.get("brand", "")
        review_count = self.product.get("review_count", "")

        intro = f"""Trying to figure out if the **{title}** is actually any good? You're probably seeing it all over Amazon{f" with {review_count}+ reviews" if review_count else ""}, and wondering if it lives up to the hype.

I dug through dozens of actual owner reviews, Reddit discussions, and YouTube videos to find out what real people think after months of using this thing—not just the honeymoon-period takes.

Here's what I found."""

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
        """Generate quick verdict summary."""
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        rating = self.product.get("rating", "4")
        price = self.product.get("price", "")

        # Adjust verdict based on rating
        try:
            rating_val = float(rating)
        except:
            rating_val = 4.0

        if rating_val >= 4.5:
            verdict_tone = "genuinely impressed"
            recommend = "solid yes for most people"
        elif rating_val >= 4.0:
            verdict_tone = "pleasantly surprised"
            recommend = "worth considering"
        else:
            verdict_tone = "mixed"
            recommend = "depends on your specific needs"

        verdict = f"""## The Quick Verdict

After going through everything, I'm {verdict_tone} by the {title}. It's a {recommend}.

The {f"{price} price point" if price else "price"} puts it in competition with some solid alternatives, but it holds its own. More on that below."""

        return verdict

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
        """Generate pros and cons section."""
        title = self.product.get("title", "this product")
        features = self.product.get("features", [])
        rating = self.product.get("rating", "4")

        # TODO: In production, these would come from web research
        # For now, generate placeholder structure

        section = """## What Real Owners Say: The Good and Bad

I went through hundreds of reviews and Reddit threads. Here's what keeps coming up:

{{< pros-cons >}}
PROS:
- [RESEARCH: Add specific pro from Reddit/reviews]
- [RESEARCH: Add specific pro from YouTube comments]
- [RESEARCH: Add specific pro from Amazon reviews]

CONS:
- [RESEARCH: Add specific con from Reddit/reviews]
- [RESEARCH: Add specific con - common complaint]
- [RESEARCH: Add limitation or gotcha]
{{< /pros-cons >}}

**Note to editor:** Replace the bracketed items with actual findings from research. Look for specific, repeated feedback—not vague generalizations."""

        return section

    def _generate_who_should_buy(self) -> str:
        """Generate who should/shouldn't buy section."""
        title = self.product.get("title", "this product")
        category = self.product.get("category", "product")
        price = self.product.get("price", "")

        section = f"""## Who Should Buy the {title}

This is a good fit if you:

- [RESEARCH: Ideal use case #1 from reviews]
- [RESEARCH: Ideal use case #2]
- [RESEARCH: Specific user type who benefits most]

## Who Should Skip It

Don't buy this if:

- [RESEARCH: Specific scenario where this fails]
- [RESEARCH: User type who would be disappointed]
- [RESEARCH: If you need X feature, look elsewhere]

**Note to editor:** Fill in based on actual review research. Be specific—vague advice helps no one."""

        return section

    def _generate_comparison(self) -> str:
        """Generate competitor comparison section."""
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        price = self.product.get("price", "")
        category = self.product.get("category", "")

        section = f"""## How It Compares to Alternatives

{{{{< comparison-table >}}}}
| Feature | {title[:30]} | [Competitor A] | [Competitor B] |
|---------|--------------|----------------|----------------|
| Price | {price} | [Price] | [Price] |
| [Key Spec] | [Value] | [Value] | [Value] |
| [Key Spec] | [Value] | [Value] | [Value] |
| Rating | {self.product.get('rating', 'N/A')}/5 | [Rating] | [Rating] |
{{{{< /comparison-table >}}}}

**{title}** is the better choice if you prioritize [X]. Go with **[Competitor A]** if you need [Y] instead.

**Note to editor:** Research 1-2 actual competitors and fill in real specs."""

        return section

    def _generate_image_gallery(self) -> str:
        """Generate gallery of additional product images."""
        if len(self.images) <= 1:
            return ""

        gallery = """## Product Images

"""
        for i, img in enumerate(self.images[1:], start=2):
            gallery += f"""![{img['alt']}]({img['local_path']})

"""
        return gallery

    def _generate_verdict(self) -> str:
        """Generate final verdict and CTA."""
        title = self.product.get("title", "this product")
        price = self.product.get("price", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")
        affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={tag}"
        rating = self.product.get("rating", "4")

        try:
            rating_val = float(rating)
        except:
            rating_val = 4.0

        if rating_val >= 4.3:
            confidence = "confident recommendation"
            cta_text = "Check Current Price on Amazon"
        elif rating_val >= 3.8:
            confidence = "solid option for the right buyer"
            cta_text = "See It on Amazon"
        else:
            confidence = "has its place, but do your homework"
            cta_text = "View on Amazon"

        section = f"""## Final Verdict: Should You Buy the {title}?

The {title} is a {confidence}.

If you've read this far and it checks your boxes, you'll probably be happy with it. The {f"${price.replace('$', '')} " if price and '$' in price else ""}price is reasonable for what you get, and the consistent positive feedback from long-term owners backs that up.

[RESEARCH: Add one specific, compelling reason from your research]

{{{{< affiliate-link url="{affiliate_link}" text="{cta_text}" >}}}}"""

        return section

    def _generate_faq(self) -> str:
        """Generate FAQ section for long-tail keywords."""
        title = self.product.get("title", "this product")
        brand = self.product.get("brand", "")
        category = self.product.get("category", "product")
        price = self.product.get("price", "")
        asin = self.product.get("asin", "")
        tag = self.product.get("affiliate_tag", "amazonfi08e0c-20")

        section = f"""## Frequently Asked Questions

### Is the {title} worth the money?

[RESEARCH: Answer based on value-for-money analysis from reviews. Be specific about what you get for the price.]

### How long does the {title} last?

[RESEARCH: Look for durability feedback from long-term owners on Reddit and Amazon. Quote specific timeframes if available.]

### What's the warranty on the {title}?

[RESEARCH: Find actual warranty information. Most Amazon products have manufacturer warranty details in the listing.]

### {title} vs [Top Competitor] — which is better?

[RESEARCH: Direct comparison based on your research. Be opinionated—don't fence-sit.]

### Where can I get the best price on the {title}?

Amazon typically has the best price, and Prime members get free shipping. Prices fluctuate, so check the current deal:

{{{{< affiliate-link url="https://www.amazon.com/dp/{asin}?tag={tag}" text="Check Current Amazon Price" >}}}}

---

**Note to editor:** Replace [RESEARCH] placeholders with actual findings. Use Google's "People Also Ask" for this product to find real questions people are searching for."""

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

    # Download images
    images = []
    if not args.no_images and product_data.get("images"):
        print(f"\n📸 Downloading product images...")
        slug = slugify(product_data.get("title", "product"), max_length=40)
        images = fetcher.download_images(slug)
        print(f"   Downloaded {len(images)} images")

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
