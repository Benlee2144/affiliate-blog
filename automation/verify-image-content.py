#!/usr/bin/env python3
"""
Image Content Verification using AI Vision
Verifies that downloaded product images actually show the expected product
"""
import sys
import os
import json
import base64
import urllib.request

def get_image_base64(image_path):
    """Read image file and return base64 encoded string"""
    with open(image_path, 'rb') as f:
        return base64.standard_b64encode(f.read()).decode('utf-8')

def verify_image_content(image_path, expected_product):
    """
    Use OpenAI Vision API to verify image shows expected product
    Returns: (is_correct, actual_description)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("WARNING: No OPENAI_API_KEY set, skipping AI verification")
        return True, "Skipped (no API key)"
    
    # Read and encode image
    try:
        image_data = get_image_base64(image_path)
    except Exception as e:
        return False, f"Failed to read image: {e}"
    
    # Determine content type
    ext = os.path.splitext(image_path)[1].lower()
    content_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
    
    # Build API request
    prompt = f"""Look at this product image and answer TWO questions:

1. What product is shown in this image? Be specific (brand, type, color if visible).
2. Is this a "{expected_product}"? Answer YES or NO.

Format your response as:
PRODUCT: [what you see]
MATCH: [YES or NO]
REASON: [brief explanation if NO]"""
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{image_data}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 200
    }
    
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=data,
        headers=headers
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse response
            is_match = 'MATCH: YES' in content.upper() or 'MATCH:YES' in content.upper()
            
            # Extract product description
            product_line = [l for l in content.split('\n') if l.startswith('PRODUCT:')]
            product_desc = product_line[0].replace('PRODUCT:', '').strip() if product_line else "Unknown"
            
            return is_match, product_desc
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return False, f"API error: {e.code} - {error_body[:100]}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    if len(sys.argv) < 3:
        print("Usage: verify-image-content.py <image_path> <expected_product>")
        print("Example: verify-image-content.py cuisinart-sm50.jpg 'Cuisinart stand mixer'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    expected_product = sys.argv[2]
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"Verifying: {image_path}")
    print(f"Expected: {expected_product}")
    
    is_correct, description = verify_image_content(image_path, expected_product)
    
    if is_correct:
        print(f"✅ MATCH: {description}")
        sys.exit(0)
    else:
        print(f"❌ MISMATCH!")
        print(f"   Expected: {expected_product}")
        print(f"   Got: {description}")
        sys.exit(1)


if __name__ == "__main__":
    main()
