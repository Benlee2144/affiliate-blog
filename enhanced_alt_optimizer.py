#!/usr/bin/env python3
"""
Enhanced alt text optimizer to catch any remaining basic alt text.
This script improves alt text that might have been missed in the first pass.
"""

import os
import re
import glob
from pathlib import Path

def smart_enhance_alt_text(current_alt, image_path, context=""):
    """
    Enhanced alt text improvement using pattern recognition and keyword extraction.
    """
    
    # Skip if already long and descriptive
    if len(current_alt.strip()) > 60 and any(word in current_alt.lower() for word in ['with', 'showing', 'featuring', 'display', 'design', 'sensor', 'battery', 'capacity']):
        return current_alt
    
    # Extract product info from filename and alt text
    filename = os.path.basename(image_path).replace('.jpg', '').replace('.png', '').replace('-', ' ')
    filename_clean = re.sub(r'\d+$', '', filename).strip()
    
    # Common product categories and their descriptors
    category_descriptors = {
        'vacuum': ['with HEPA filtration', 'cordless design and lightweight construction', 'featuring cyclonic suction technology'],
        'headphones': ['with active noise cancellation', 'featuring wireless Bluetooth connectivity', 'with over-ear design and premium sound'],
        'speaker': ['with Bluetooth 5.0 and waterproof design', 'featuring 360-degree sound', 'with portable wireless design'],
        'tablet': ['with high-resolution display and slim profile', 'featuring touch screen and premium build', 'with stylus support and long battery life'],
        'laptop': ['with backlit keyboard and premium design', 'featuring slim profile and all-day battery', 'with high-performance processors'],
        'monitor': ['with 4K resolution and ultra-wide display', 'featuring HDR support and slim bezels', 'with adjustable stand and gaming features'],
        'keyboard': ['with mechanical switches and RGB lighting', 'featuring ergonomic design and programmable keys', 'with wireless connectivity'],
        'mouse': ['with precision sensor and ergonomic design', 'featuring wireless connectivity and long battery', 'with programmable buttons'],
        'camera': ['with interchangeable lenses and 4K video', 'featuring image stabilization and pro features', 'with weather sealing and dual pixel autofocus'],
        'microphone': ['with USB connectivity and professional sound quality', 'featuring cardioid pickup pattern and zero-latency monitoring', 'with broadcast-quality audio'],
        'blender': ['with powerful motor and variable speed control', 'featuring stainless steel blades and large capacity', 'with preset programs and self-cleaning'],
        'cooker': ['with multiple cooking functions and timer', 'featuring non-stick interior and safety features', 'with programmable settings'],
        'fryer': ['with digital controls and oil-free cooking', 'featuring rapid air circulation technology', 'with multiple cooking presets'],
        'coffee': ['with programmable brewing and thermal carafe', 'featuring built-in grinder and strength control', 'with auto-shutoff and keep-warm plate'],
        'grill': ['with temperature control and even heating', 'featuring porcelain-enameled cooking grates', 'with built-in thermometer'],
        'scale': ['with digital display and precision measurement', 'featuring tare function and multiple units', 'with sleek design and easy cleanup'],
        'thermometer': ['with instant-read display and waterproof design', 'featuring accurate temperature sensing', 'with backlit screen and probe'],
        'humidifier': ['with ultrasonic technology and quiet operation', 'featuring large tank capacity and auto-shutoff', 'with essential oil diffuser'],
        'purifier': ['with HEPA filtration and air quality monitor', 'featuring quiet operation and multiple speeds', 'with smart controls and app connectivity'],
        'toaster': ['with multiple browning settings and wide slots', 'featuring even heating and compact design', 'with removable crumb tray'],
        'mixer': ['with powerful motor and multiple attachments', 'featuring tilt-head design and large bowl', 'with variable speed control'],
        'processor': ['with multiple blades and large capacity', 'featuring pulse function and safety lock', 'with dishwasher-safe parts'],
        'kettle': ['with rapid boiling and auto-shutoff', 'featuring temperature control and keep-warm', 'with cordless design and LED indicator'],
        'iron': ['with steam function and non-stick soleplate', 'featuring vertical steaming and anti-drip', 'with auto-shutoff safety'],
        'dryer': ['with multiple heat settings and ionic technology', 'featuring lightweight design and professional results', 'with concentrator nozzle'],
        'massager': ['with multiple speed settings and ergonomic grip', 'featuring deep tissue percussion therapy', 'with interchangeable attachments'],
        'projector': ['with 4K resolution and bright display', 'featuring portable design and wireless connectivity', 'with keystone correction'],
        'hub': ['with multiple ports and fast data transfer', 'featuring compact aluminum design', 'with power delivery and 4K support'],
        'ssd': ['with fast read/write speeds and portable design', 'featuring USB-C connectivity and shock resistance', 'with encryption and durability'],
        'charger': ['with fast charging and multiple device support', 'featuring compact design and safety protection', 'with LED status indicators'],
        'stand': ['with adjustable height and ergonomic positioning', 'featuring sturdy aluminum construction', 'with cable management'],
        'light': ['with adjustable brightness and color temperature', 'featuring LED technology and energy efficiency', 'with flexible positioning arm'],
        'fan': ['with quiet operation and multiple speed settings', 'featuring oscillation and remote control', 'with energy-efficient motor'],
        'heater': ['with adjustable temperature and safety features', 'featuring ceramic heating and tip-over protection', 'with remote control'],
        'doorbell': ['with HD video and two-way audio', 'featuring motion detection and cloud storage', 'with smartphone app control'],
        'thermostat': ['with smart learning and energy savings', 'featuring touchscreen display and WiFi connectivity', 'with scheduling and remote control'],
        'plug': ['with smart controls and voice activation', 'featuring energy monitoring and scheduling', 'with compact design'],
        'tracker': ['with heart rate monitoring and GPS', 'featuring sleep tracking and smartphone notifications', 'with long battery life'],
        'watch': ['with fitness tracking and smartphone integration', 'featuring always-on display and health monitoring', 'with water resistance'],
        'reader': ['with high-resolution display and adjustable backlight', 'featuring long battery life and lightweight design', 'with waterproof construction'],
        'phone': ['with advanced camera system and premium build', 'featuring fast performance and all-day battery', 'with wireless charging support'],
        'case': ['with premium materials and perfect fit', 'featuring wireless charging compatibility', 'with military-grade protection'],
    }
    
    # Find matching category
    alt_lower = current_alt.lower()
    filename_lower = filename_clean.lower()
    
    matched_descriptors = []
    for category, descriptors in category_descriptors.items():
        if category in alt_lower or category in filename_lower:
            matched_descriptors = descriptors
            break
    
    # If no specific category match, use generic improvements
    if not matched_descriptors:
        if any(word in alt_lower for word in ['pro', 'plus', 'max', 'ultra']):
            matched_descriptors = ['with professional features and premium build quality', 'featuring advanced technology and superior performance']
        else:
            matched_descriptors = ['with quality construction and reliable performance', 'featuring user-friendly design and practical functionality']
    
    # Create enhanced alt text
    if len(current_alt.strip()) < 50:
        # Add the first descriptor that fits
        descriptor = matched_descriptors[0] if matched_descriptors else 'with premium design and reliable performance'
        enhanced_alt = f"{current_alt} {descriptor}"
        
        # Clean up and ensure it's not too long
        if len(enhanced_alt) > 120:
            enhanced_alt = enhanced_alt[:120].rsplit(' ', 1)[0]
        
        return enhanced_alt
    
    return current_alt

def process_markdown_file_enhanced(filepath):
    """
    Enhanced processing for remaining basic alt text.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Process cover image alt text
    cover_pattern = r'(cover:\s*\n(?:.*\n)*?)\s*alt:\s*"([^"]*)"'
    def enhance_cover_alt(match):
        nonlocal changes_made
        prefix = match.group(1)
        current_alt = match.group(2)
        
        image_match = re.search(r'image:\s*"([^"]*)"', prefix)
        image_path = image_match.group(1) if image_match else ""
        
        enhanced_alt = smart_enhance_alt_text(current_alt, image_path)
        if enhanced_alt != current_alt:
            changes_made = True
            return f'{prefix}alt: "{enhanced_alt}"'
        return match.group(0)
    
    content = re.sub(cover_pattern, enhance_cover_alt, content, flags=re.MULTILINE)
    
    # Process inline markdown images
    inline_pattern = r'!\[([^\]]*)\]\(([^)]+)\)(?:\s*"[^"]*")?'
    def enhance_inline_alt(match):
        nonlocal changes_made
        current_alt = match.group(1)
        image_path = match.group(2)
        
        enhanced_alt = smart_enhance_alt_text(current_alt, image_path)
        if enhanced_alt != current_alt:
            changes_made = True
            return f'![{enhanced_alt}]({image_path})'
        return match.group(0)
    
    content = re.sub(inline_pattern, enhance_inline_alt, content)
    
    # Write back if changes were made
    if changes_made:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """
    Enhanced processing for remaining posts.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    post_files = glob.glob("content/posts/*.md")
    
    print(f"Running enhanced optimization on {len(post_files)} posts...")
    
    files_changed = 0
    
    for filepath in post_files:
        if process_markdown_file_enhanced(filepath):
            files_changed += 1
            print(f"Enhanced: {os.path.basename(filepath)}")
    
    print(f"\n✅ Enhanced optimization complete! Improved {files_changed} additional files.")

if __name__ == "__main__":
    main()