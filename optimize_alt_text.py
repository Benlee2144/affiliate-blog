#!/usr/bin/env python3
"""
Optimize all image alt text across the affiliate blog for SEO.
This script improves both inline markdown images and cover image alt text.
"""

import os
import re
import glob
from pathlib import Path

def improve_alt_text(current_alt, image_path, context=""):
    """
    Improve alt text to be more descriptive and SEO-friendly.
    """
    # Common product patterns and improvements
    improvements = {
        # Air fryers
        r"Ninja DualZone 8QT air fryer": "Ninja DualZone DZ201 8-quart dual basket air fryer with digital display",
        r"Ninja DualZone interior baskets": "Ninja DualZone dual basket air fryer interior showing two separate cooking chambers",
        r"Cosori Pro air fryer": "Cosori Pro LE 5.8-quart air fryer with digital touchscreen and stainless steel finish",
        r"Cosori Pro air fryer interior": "Cosori Pro air fryer interior basket with non-stick coating and spacious cooking chamber",
        r"Instant Vortex Plus 6QT air fryer": "Instant Vortex Plus 6-quart air fryer with digital control panel and viewing window",
        r"Instant Vortex Plus control panel": "Instant Vortex Plus air fryer digital control panel with preset cooking functions",
        
        # Espresso machines
        r"De'Longhi Stilosa espresso machine": "De'Longhi Stilosa manual espresso machine with stainless steel boiler and steam wand",
        r"Breville Bambino Plus espresso machine": "Breville Bambino Plus automatic espresso machine with milk frother and compact design",
        r"Gaggia Classic Pro espresso machine": "Gaggia Classic Pro semi-automatic espresso machine with commercial-style group head",
        r"Breville Barista Express Impress espresso machine": "Breville Barista Express Impress espresso machine with built-in conical burr grinder",
        
        # Thermometers
        r"ThermoWorks Thermapen ONE": "ThermoWorks Thermapen ONE instant-read meat thermometer with rotating display and waterproof design",
        r"ThermoPro TP19H meat thermometer": "ThermoPro TP19H digital instant-read meat thermometer with backlit display and fold-away probe",
        r"Lavatools Javelin Pro Duo thermometer": "Lavatools Javelin Pro Duo digital meat thermometer with dual temperature sensors",
        r"MEATER Plus wireless thermometer": "MEATER Plus wireless meat thermometer with Bluetooth connectivity for remote monitoring",
        
        # Humidifiers
        r"Dreo HM311S humidifier": "Dreo HM311S ultrasonic humidifier with 4-liter tank and essential oil tray for bedrooms",
        r"Carepod One humidifier": "Carepod One stainless steel ultrasonic humidifier with easy-fill design and quiet operation",
        r"Levoit LV600S humidifier": "Levoit LV600S hybrid ultrasonic humidifier with warm and cool mist settings and remote control",
        
        # Kitchen scales
        r"OXO Good Grips 11-Pound kitchen scale": "OXO Good Grips 11-pound digital kitchen scale with pull-out display and non-slip base",
        r"Escali Primo digital kitchen scale": "Escali Primo P115C digital kitchen scale in polished chrome with tare function",
        r"MyWeigh KD-8000 bakers math kitchen scale": "MyWeigh KD-8000 baker's math kitchen scale with percentage weighing and stainless steel platform",
        r"Ozeri Pronto digital kitchen scale": "Ozeri Pronto digital multifunction kitchen scale with elegant black tempered glass platform",
        
        # USB-C Hubs
        r"Anker 555 USB-C Hub": "Anker PowerExpand+ 555 USB-C hub with 8-in-1 connectivity and 100W power delivery",
        r"Plugable 9-in-1 USB-C Hub": "Plugable UD-ULTCDL 9-in-1 USB-C hub with dual 4K HDMI and 100W charging",
        r"Satechi Pro Hub Max": "Satechi Pro Hub Max aluminum USB-C hub with magnetic attachment for MacBook",
        
        # SSDs
        r"Samsung T9 portable SSD": "Samsung T9 portable SSD 2TB with USB 3.2 Gen 2x2 interface and shock-resistant design",
        r"Crucial X10 Pro portable SSD": "Crucial X10 Pro portable SSD with rugged design and up to 2,100 MB/s read speeds",
        r"SanDisk Extreme Pro V2 portable SSD": "SanDisk Extreme Pro Portable SSD V2 with IP65 water and dust resistance",
        
        # Gaming mice
        r"Razer Viper V3 Pro wireless gaming mouse": "Razer Viper V3 Pro wireless gaming mouse with Focus Pro 30K sensor and 90-hour battery",
        r"Logitech G Pro X Superlight 2": "Logitech G Pro X Superlight 2 wireless gaming mouse in white with HERO 25K sensor",
        r"Razer DeathAdder V3 HyperSpeed": "Razer DeathAdder V3 HyperSpeed wireless gaming mouse with ergonomic right-handed design",
        
        # Audio
        r"JBL Flip 6 Speaker": "JBL Flip 6 portable Bluetooth speaker with PartyBoost and IP67 waterproof rating",
        r"Apple AirPods Pro 3": "Apple AirPods Pro 3rd generation with USB-C case and adaptive transparency mode",
        r"AirPods Pro 3 extended use": "Apple AirPods Pro 3 shown during extended listening session with active noise cancellation",
        
        # General patterns - catch remaining basic alt text
        r"^([A-Z][a-zA-Z0-9\s&\-]+)$": lambda m: f"{m.group(1)} product image with detailed view and professional lighting",
    }
    
    # Apply specific improvements
    for pattern, replacement in improvements.items():
        if callable(replacement):
            match = re.search(pattern, current_alt)
            if match:
                return replacement(match)
        elif re.search(pattern, current_alt, re.IGNORECASE):
            return replacement
    
    # If no specific improvement found, make it more descriptive
    if len(current_alt.strip()) < 30:
        # Extract product info from image path if possible
        path_parts = image_path.split('/')
        if 'products' in path_parts:
            filename = path_parts[-1].replace('.jpg', '').replace('.png', '').replace('-', ' ')
            # Capitalize words
            filename_words = [word.capitalize() for word in filename.split()]
            improved = f"{' '.join(filename_words)} product showcase with detailed features and premium finish"
            return improved
    
    return current_alt

def process_markdown_file(filepath):
    """
    Process a single markdown file to improve all image alt text.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Process cover image alt text in frontmatter
    cover_pattern = r'(cover:\s*\n(?:.*\n)*?)\s*alt:\s*"([^"]*)"'
    def improve_cover_alt(match):
        nonlocal changes_made
        prefix = match.group(1)
        current_alt = match.group(2)
        
        # Extract image path for context
        image_match = re.search(r'image:\s*"([^"]*)"', prefix)
        image_path = image_match.group(1) if image_match else ""
        
        improved_alt = improve_alt_text(current_alt, image_path)
        if improved_alt != current_alt:
            changes_made = True
            return f'{prefix}alt: "{improved_alt}"'
        return match.group(0)
    
    content = re.sub(cover_pattern, improve_cover_alt, content, flags=re.MULTILINE)
    
    # Process inline markdown images
    inline_pattern = r'!\[([^\]]*)\]\(([^)]+)\)(?:\s*"[^"]*")?'
    def improve_inline_alt(match):
        nonlocal changes_made
        current_alt = match.group(1)
        image_path = match.group(2)
        
        improved_alt = improve_alt_text(current_alt, image_path)
        if improved_alt != current_alt:
            changes_made = True
            return f'![{improved_alt}]({image_path})'
        return match.group(0)
    
    content = re.sub(inline_pattern, improve_inline_alt, content)
    
    # Write back if changes were made
    if changes_made:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """
    Process all markdown files in the blog.
    """
    os.chdir("/Users/benjaminarp/Desktop/amazon website/affiliate-blog/")
    
    # Get all markdown files in content/posts/
    post_files = glob.glob("content/posts/*.md")
    
    print(f"Found {len(post_files)} posts to process...")
    
    files_changed = 0
    total_files = len(post_files)
    
    for i, filepath in enumerate(post_files, 1):
        print(f"Processing {i}/{total_files}: {os.path.basename(filepath)}")
        
        if process_markdown_file(filepath):
            files_changed += 1
    
    print(f"\n✅ Complete! Updated alt text in {files_changed} files out of {total_files} total.")
    print(f"Files unchanged: {total_files - files_changed}")

if __name__ == "__main__":
    main()