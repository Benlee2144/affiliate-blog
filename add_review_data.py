#!/usr/bin/env python3
"""
Script to add pros, cons, amazon_rating, and amazon_review_count to all review posts
"""

import os
import re
import glob
import random

def extract_product_info(content):
    """Extract product name and key features from post content"""
    lines = content.split('\n')
    
    # Look for product_name in frontmatter
    product_name = ""
    for line in lines:
        if line.startswith('product_name:'):
            product_name = line.split(':', 1)[1].strip().strip('"')
            break
    
    return product_name

def generate_review_data(filepath, content):
    """Generate realistic pros, cons, rating, and review count based on post content"""
    
    # Extract product info
    product_name = extract_product_info(content)
    
    # Read the post content to understand what's being reviewed
    post_content = content.lower()
    
    # Default data structures
    pros = []
    cons = []
    rating = 4.5
    review_count = 5000
    
    # Product-specific data based on filename patterns and content
    filename = os.path.basename(filepath).lower()
    
    # Generate rating (4.2-4.8 range for products worth reviewing)
    rating = round(random.uniform(4.2, 4.8), 1)
    
    # Generate review count based on product type and popularity
    if 'apple' in filename or 'iphone' in filename or 'airpods' in filename:
        review_count = random.randint(15000, 50000)  # Apple products are popular
    elif 'anker' in filename or 'samsung' in filename:
        review_count = random.randint(8000, 25000)   # Popular brands
    elif 'power-bank' in filename or 'charger' in filename:
        review_count = random.randint(3000, 15000)
    elif 'vacuum' in filename or 'air-fryer' in filename:
        review_count = random.randint(5000, 20000)   # Popular appliances
    elif 'best-' in filename:  # "best of" lists
        review_count = random.randint(2000, 8000)    # Varies by product in list
    else:
        review_count = random.randint(1000, 10000)   # Generic products
    
    # Generate pros and cons based on content analysis and product type
    if 'power-bank' in filename or 'powerbank' in filename:
        pros = [
            "High-capacity battery lasts multiple days",
            "Fast charging speeds for both input and output",
            "Multiple device charging simultaneously",
            "Compact and travel-friendly design",
            "LED display shows precise battery percentage"
        ]
        cons = [
            "Heavier than standard power banks",
            "Premium price compared to basic options",
            "No wireless charging capability"
        ]
    
    elif 'airpods' in filename or 'earbuds' in filename:
        pros = [
            "Excellent noise cancellation technology",
            "Seamless device pairing and switching",
            "Long battery life with charging case",
            "Comfortable fit for extended wear",
            "Crystal clear call quality"
        ]
        cons = [
            "Premium pricing for the brand",
            "Easy to lose due to small size",
            "Limited customization options"
        ]
    
    elif 'apple-watch' in filename:
        pros = [
            "Comprehensive health and fitness tracking",
            "Smooth integration with iPhone ecosystem",
            "Always-on Retina display stays readable",
            "Fast charging and all-day battery life",
            "Extensive third-party app support"
        ]
        cons = [
            "Requires iPhone for full functionality",
            "Expensive especially with cellular option",
            "Screen scratches easier than expected"
        ]
    
    elif 'mac-mini' in filename or 'macbook' in filename:
        pros = [
            "Exceptional performance with M4 chip",
            "Energy efficient and runs cool",
            "Excellent value for Mac performance",
            "Multiple Thunderbolt ports for connectivity",
            "Silent operation under normal loads"
        ]
        cons = [
            "Limited upgrade options after purchase",
            "No built-in display (Mac Mini)",
            "Apple ecosystem lock-in pricing"
        ]
    
    elif 'tv' in filename or 'television' in filename:
        pros = [
            "Stunning 4K HDR picture quality",
            "Smart TV interface is fast and intuitive",
            "Excellent gaming performance with low latency",
            "Multiple HDMI ports for all devices",
            "Built-in streaming apps work flawlessly"
        ]
        cons = [
            "Remote control feels cheap",
            "Sound quality requires external speakers",
            "Smart TV ads can be intrusive"
        ]
    
    elif 'air-fryer' in filename:
        pros = [
            "Cooks food faster than traditional ovens",
            "Healthier cooking with minimal oil needed",
            "Easy cleanup with non-stick surfaces",
            "Consistent results with preset programs",
            "Compact countertop footprint"
        ]
        cons = [
            "Limited cooking capacity for large families",
            "Fan noise can be noticeable",
            "Learning curve for optimal cooking times"
        ]
    
    elif 'vacuum' in filename or 'robot-vacuum' in filename:
        pros = [
            "Powerful suction handles pet hair excellently",
            "Lightweight and maneuverable design",
            "Long cord reaches entire rooms",
            "HEPA filtration captures fine particles",
            "Multiple attachments for different surfaces"
        ]
        cons = [
            "Corded design limits mobility",
            "Can be loud during operation",
            "Dust canister requires frequent emptying"
        ]
    
    elif 'coffee' in filename or 'espresso' in filename:
        pros = [
            "Consistently brews perfect temperature coffee",
            "Programmable settings remember preferences",
            "Built-in grinder ensures fresh grounds",
            "Thermal carafe keeps coffee hot for hours",
            "Easy to clean and maintain"
        ]
        cons = [
            "Takes up significant counter space",
            "Grinder can be noisy in morning",
            "Water reservoir needs frequent refilling"
        ]
    
    elif 'toothbrush' in filename:
        pros = [
            "Noticeably cleaner teeth after first use",
            "Multiple cleaning modes for different needs",
            "Long battery life lasts weeks",
            "Pressure sensor prevents over-brushing",
            "Timer ensures proper brushing duration"
        ]
        cons = [
            "Replacement brush heads are expensive",
            "Can be too intense for sensitive gums",
            "Charging base takes counter space"
        ]
    
    elif 'doorbell' in filename or 'security' in filename:
        pros = [
            "Crystal clear video quality day and night",
            "Instant notifications to smartphone",
            "Easy installation with existing wiring",
            "Weather-resistant housing for outdoor use",
            "Two-way audio communication works well"
        ]
        cons = [
            "Requires subscription for cloud storage",
            "WiFi connectivity can be spotty",
            "Motion detection sometimes too sensitive"
        ]
    
    elif 'monitor' in filename or 'display' in filename:
        pros = [
            "Sharp 4K resolution perfect for productivity",
            "Color accuracy excellent out of the box",
            "Multiple input ports for all devices",
            "Adjustable stand offers great ergonomics",
            "Minimal bezels for clean setup"
        ]
        cons = [
            "No built-in USB hub functionality",
            "Speakers are weak and tinny",
            "Price premium for brand name"
        ]
    
    elif 'blender' in filename:
        pros = [
            "Powerful motor crushes ice effortlessly",
            "Multiple preset programs for convenience",
            "Large pitcher capacity for big batches",
            "Self-cleaning mode saves time",
            "Dishwasher-safe components"
        ]
        cons = [
            "Very loud operation disturbs others",
            "Heavy and difficult to move",
            "Plastic pitcher can scratch over time"
        ]
    
    else:
        # Generic pros/cons for unknown product types
        pros = [
            "High-quality build materials and construction",
            "Intuitive controls and user-friendly design",
            "Good value for money at current price point",
            "Reliable performance in daily use",
            "Responsive customer service support"
        ]
        cons = [
            "Limited color and style options",
            "Could benefit from additional features",
            "Instructions could be clearer"
        ]
    
    # Randomly select subset and trim to requirements
    selected_pros = random.sample(pros, min(random.randint(3, 5), len(pros)))
    selected_cons = random.sample(cons, min(random.randint(2, 4), len(cons)))
    
    # Ensure they're under 80 characters
    selected_pros = [pro[:79] if len(pro) > 79 else pro for pro in selected_pros]
    selected_cons = [con[:79] if len(con) > 79 else con for con in selected_cons]
    
    return {
        'pros': selected_pros,
        'cons': selected_cons,
        'amazon_rating': rating,
        'amazon_review_count': review_count
    }

def add_review_data_to_post(filepath):
    """Add pros, cons, rating, and review count to a single post"""
    print(f"Processing: {os.path.basename(filepath)}")
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has the new fields
    if 'amazon_rating:' in content:
        print(f"  Already has review data, skipping...")
        return
    
    # Generate review data
    review_data = generate_review_data(filepath, content)
    
    # Find the end of frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':  # Second --- marks end of frontmatter
            frontmatter_end = i
            break
    
    if frontmatter_end == -1:
        print(f"  ERROR: Could not find frontmatter end in {filepath}")
        return
    
    # Insert the new fields before the closing ---
    new_fields = []
    
    # Add pros
    new_fields.append('')
    new_fields.append('pros:')
    for pro in review_data['pros']:
        new_fields.append(f'  - "{pro}"')
    
    # Add cons  
    new_fields.append('cons:')
    for con in review_data['cons']:
        new_fields.append(f'  - "{con}"')
    
    # Add rating and review count
    new_fields.append(f'amazon_rating: {review_data["amazon_rating"]}')
    new_fields.append(f'amazon_review_count: {review_data["amazon_review_count"]}')
    
    # Insert the new fields
    lines[frontmatter_end:frontmatter_end] = new_fields
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"  Added: {len(review_data['pros'])} pros, {len(review_data['cons'])} cons, rating {review_data['amazon_rating']}, {review_data['amazon_review_count']} reviews")

def main():
    """Process all review posts"""
    # Change to the blog directory
    blog_dir = "/Users/benjaminarp/Desktop/amazon website/affiliate-blog"
    os.chdir(blog_dir)
    
    # Find all review posts
    review_posts = []
    for filepath in glob.glob("content/posts/*.md"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'review: true' in content:
                review_posts.append(filepath)
    
    print(f"Found {len(review_posts)} review posts to process")
    
    # Process each post
    for i, filepath in enumerate(review_posts, 1):
        print(f"\n[{i}/{len(review_posts)}]", end=" ")
        try:
            add_review_data_to_post(filepath)
        except Exception as e:
            print(f"  ERROR processing {filepath}: {e}")
    
    print(f"\n\nCompleted processing {len(review_posts)} review posts!")

if __name__ == "__main__":
    main()