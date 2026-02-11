#!/bin/bash
# Auto Blog Generator for Researched Picks
# Runs Claude Code to create comparison blog posts with natural timing

# Configuration
BLOG_DIR="/Users/benjaminarp/Desktop/amazon website/affiliate-blog"
TOPICS_FILE="$BLOG_DIR/automation/topics.txt"
LOG_FILE="$BLOG_DIR/automation/blog.log"
POSTS_DIR="$BLOG_DIR/content/posts"
CLAUDE_PATH="claude"  # Update this if claude is in a different location

# Create log file if it doesn't exist
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Check if a similar post already exists
check_duplicate() {
    local TOPIC="$1"
    # Extract key words from topic (e.g., "Standing Desks" from "Best Standing Desks for Home Office 2026")
    KEYWORDS=$(echo "$TOPIC" | sed 's/Best //; s/ for.*//; s/ 2026//' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

    # Check if any post contains these keywords
    if ls "$POSTS_DIR"/*.md 2>/dev/null | xargs grep -l -i "$KEYWORDS" >/dev/null 2>&1; then
        log "WARNING: Similar post may exist for '$KEYWORDS'"
        return 1
    fi

    # Also check filename patterns
    if ls "$POSTS_DIR"/*${KEYWORDS}*.md 2>/dev/null >/dev/null; then
        log "WARNING: Post with similar filename exists for '$KEYWORDS'"
        return 1
    fi

    return 0
}

# Add random delay (0-90 minutes) to make posting times look natural
random_delay() {
    DELAY=$((RANDOM % 5400))  # 0-90 minutes in seconds
    log "Adding random delay of $((DELAY / 60)) minutes for natural timing..."
    sleep $DELAY
}

# Get a random unused topic (not just the first one)
get_random_topic() {
    # Get all non-comment lines, pick one randomly
    AVAILABLE=$(grep -v "^#" "$TOPICS_FILE" | grep -v "^$")

    if [ -z "$AVAILABLE" ]; then
        log "ERROR: No more topics available! Add more to topics.txt"
        exit 1
    fi

    # Count available topics and pick random one
    COUNT=$(echo "$AVAILABLE" | wc -l)
    RANDOM_LINE=$((RANDOM % COUNT + 1))
    TOPIC=$(echo "$AVAILABLE" | sed -n "${RANDOM_LINE}p")

    echo "$TOPIC"
}

# Mark a topic as completed by adding # prefix
mark_completed() {
    local TOPIC="$1"
    # Escape special characters for sed
    ESCAPED=$(echo "$TOPIC" | sed 's/[&/\]/\\&/g')
    sed -i '' "s/^${ESCAPED}$/# [DONE] ${ESCAPED}/" "$TOPICS_FILE" 2>/dev/null || \
    sed -i "s/^${ESCAPED}$/# [DONE] ${ESCAPED}/" "$TOPICS_FILE"
}

# Verify an image file is valid (not empty, not HTML error page)
verify_image() {
    local IMG_PATH="$1"

    if [ ! -f "$IMG_PATH" ]; then
        return 1
    fi

    # Check file size (should be > 10KB for a real image)
    SIZE=$(stat -f%z "$IMG_PATH" 2>/dev/null || stat -c%s "$IMG_PATH" 2>/dev/null)
    if [ "$SIZE" -lt 10000 ]; then
        log "WARNING: Image too small (possibly placeholder): $IMG_PATH ($SIZE bytes)"
        return 1
    fi

    # Check if it's actually an image (not HTML error page)
    FILE_TYPE=$(file "$IMG_PATH" | grep -i "image\|jpeg\|png\|gif")
    if [ -z "$FILE_TYPE" ]; then
        log "WARNING: File is not a valid image: $IMG_PATH"
        return 1
    fi

    return 0
}

# Verify all images referenced in a blog post exist and are valid
verify_post_images() {
    local POST_FILE="$1"
    local IMAGES_DIR="$BLOG_DIR/static/images/products"
    local ALL_VALID=true

    log "Verifying images for: $POST_FILE"

    # Extract image paths from the post
    IMAGES=$(grep -oE '/images/products/[^"'\'')\s]+' "$POST_FILE" | sort -u)

    if [ -z "$IMAGES" ]; then
        log "WARNING: No images found in post!"
        return 1
    fi

    for IMG in $IMAGES; do
        # Convert URL path to file path
        FILE_PATH="$BLOG_DIR/static$IMG"

        if verify_image "$FILE_PATH"; then
            log "✓ Image OK: $IMG"
        else
            log "✗ Image FAILED: $IMG"
            ALL_VALID=false
        fi
    done

    if [ "$ALL_VALID" = true ]; then
        return 0
    else
        return 1
    fi
}

# Get the most recently created post
get_latest_post() {
    ls -t "$POSTS_DIR"/*.md 2>/dev/null | head -1
}

# Main execution
main() {
    log "========================================="
    log "Starting auto-blog generation..."

    # Random delay for natural timing
    random_delay

    # Try up to 5 topics to find one without duplicates
    ATTEMPTS=0
    MAX_ATTEMPTS=5

    while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
        TOPIC=$(get_random_topic)
        log "Checking topic: $TOPIC"

        if check_duplicate "$TOPIC"; then
            log "No duplicate found. Proceeding with: $TOPIC"
            break
        else
            log "Skipping duplicate topic, trying another..."
            mark_completed "$TOPIC"  # Mark as done to avoid retrying
            ATTEMPTS=$((ATTEMPTS + 1))
        fi
    done

    if [ $ATTEMPTS -eq $MAX_ATTEMPTS ]; then
        log "ERROR: Could not find a non-duplicate topic after $MAX_ATTEMPTS attempts"
        exit 1
    fi

    # Change to blog directory
    cd "$BLOG_DIR"

    # Create the prompt with writing variety instructions
    PROMPT="Create a 'Best 3' comparison blog post for: $TOPIC

IMPORTANT: First check if a similar post already exists in /content/posts/. If it does, pick a DIFFERENT topic.

Follow the CLAUDE.md instructions exactly, especially the Writing Guide section.

## WRITING STYLE - SOUND HUMAN, NOT LIKE AI

CRITICAL: Read the last 3 posts in /content/posts/ and make sure this post uses a DIFFERENT structure and opening style.

Pick ONE of these approaches RANDOMLY (don't use the same one as recent posts):
1. The Rant Start - Open annoyed about something in this category
2. The Story - Start with a scenario (buddy asked what to buy, saw Reddit complaint)
3. The Comparison Showdown - Jump straight into Product A vs B
4. The 'I Was Wrong' - Admit you expected to recommend something else
5. The Quick Answer Then Deep Dive - Answer in 2 sentences, then explain
6. The Myth Buster - Call out bad advice you keep seeing online
7. The Budget Breakdown - Frame around what you get at each price point
8. The Reddit Rabbit Hole - 'I spent 4 hours on Reddit so you don't have to'
9. The One Thing Nobody Mentions - Lead with a detail others skip
10. The Brutally Honest Teardown - Lead with everything wrong, then why you'd still buy it

Voice & Tone:
- Write like a guy talking to his friend about weekend research
- Be opinionated. Say 'I wouldn't buy this' or 'overpriced for what you get'
- Use casual language. Contractions. Sentence fragments. Start with 'And' or 'But' or 'Look,'
- Swear lightly if it fits (damn, hell)
- Cite specific sources: 'u/CameraGuy2024 on r/videography said...'

NEVER use these phrases: game-changer, straightforward, genuinely, let's dive in, it's worth noting, at the end of the day, comprehensive, seamless, cutting-edge, top-notch, no-brainer

DON'T:
- Start with empathy paragraph ('You've been searching for the perfect...')
- Use 'honest' to describe your own review
- Give every product 4.0-4.8 rating - be more extreme
- Use same section headers as other posts
- End with 'The Bottom Line' every time

## TECHNICAL REQUIREMENTS

1. Research the category and find the top 3 products
2. Find Amazon ASINs for all 3 products
3. Download product images - TRY THESE SOURCES IN ORDER:
   - Best Buy CDN (pisces.bbystatic.com) - works for electronics
   - Amazon CDN (m.media-amazon.com) - works for most products
   - Manufacturer websites - for kitchen appliances, tools, etc.
4. Research problems/complaints for EACH product (Reddit, forums, Amazon reviews)
5. Write post with varied formatting (NOT every post needs tables, FAQ, or 'Best for/Skip if' lists)
6. Use affiliate tag: amazonfi08e0c-20 for ALL Amazon links
7. Vary CTA text - not always 'Check Price on Amazon'. Try: 'grab it here', 'current price', 'see if it's on sale'
8. Assign correct category
9. Commit and push to main branch

VERIFY IMAGES (CRITICAL - DO NOT SKIP):
- Check file size > 10KB (small files are error pages)
- Use 'file' command to verify it's JPEG/PNG
- If image fails, try different source
- Do NOT commit if any image is broken
- AFTER downloading each image, use the image analysis tool or open the file and verify it actually shows the correct product
- Common failure: Amazon returns wrong product images (monitors instead of blenders, laptops instead of vacuums)
- If ANY image shows the wrong product, delete it and re-download from a different source
- VERIFY EVERY SINGLE IMAGE MATCHES ITS PRODUCT BEFORE COMMITTING"

    log "Running Claude Code..."

    # Run Claude Code
    $CLAUDE_PATH --print -p "$PROMPT" \
        --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch,Grep,Glob" \
        2>&1 | tee -a "$LOG_FILE"

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        log "Claude finished. Verifying post..."

        # Find the newly created post
        LATEST_POST=$(get_latest_post)

        if [ -n "$LATEST_POST" ]; then
            log "Checking latest post: $LATEST_POST"

            # Verify images are valid (basic check)
            if verify_post_images "$LATEST_POST"; then
                log "Basic image checks passed."
            else
                log "WARNING: Basic image checks found issues"
            fi

            # AI Vision validation - verify images actually match products
            log "Running AI vision validation..."
            VALIDATE_RESULT=$(python3 "$BLOG_DIR/automation/validate-images.py" "$LATEST_POST" --fix 2>&1)
            echo "$VALIDATE_RESULT" >> "$LOG_FILE"
            
            if echo "$VALIDATE_RESULT" | grep -q "WRONG PRODUCT"; then
                log "WARNING: AI detected wrong product images - attempting fix"
                # Re-run with fix mode
                python3 "$BLOG_DIR/automation/validate-images.py" "$LATEST_POST" --fix 2>&1 | tee -a "$LOG_FILE"
                
                # Rebuild after fix
                cd "$BLOG_DIR" && hugo --minify 2>&1 | tail -1 >> "$LOG_FILE"
                git add -A && git commit -m "Auto-fix: corrected mismatched product images" && git push 2>&1 | tail -1 >> "$LOG_FILE"
            fi

            log "SUCCESS: Blog post created and verified for '$TOPIC'"
            mark_completed "$TOPIC"

            # Verify affiliate links
            AFFILIATE_COUNT=$(grep -c "tag=amazonfi08e0c-20" "$LATEST_POST" 2>/dev/null || echo "0")
            log "Affiliate links found: $AFFILIATE_COUNT"

            if [ "$AFFILIATE_COUNT" -lt 3 ]; then
                log "WARNING: Less than 3 affiliate links found - review post"
            fi
        else
            log "WARNING: Could not find newly created post"
        fi
    else
        log "ERROR: Failed to create blog post (exit code: $EXIT_CODE)"
    fi

    log "Finished at $(date)"
    log "========================================="
}

# Run main function
main
