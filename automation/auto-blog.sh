#!/bin/bash
# Auto Blog Generator for Researched Picks
# Runs Claude Code to create comparison blog posts with natural timing

# Configuration
BLOG_DIR="/home/user/affiliate-blog"
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

    # Create the prompt with multiple image source instructions
    PROMPT="Create a 'Best 3' comparison blog post for: $TOPIC

IMPORTANT: First check if a similar post already exists in /content/posts/. If it does, pick a DIFFERENT topic.

Follow the CLAUDE.md instructions exactly:
1. Research the category and find the top 3 products
2. Find Amazon ASINs for all 3 products
3. Download product images - TRY THESE SOURCES IN ORDER:
   - Best Buy CDN (pisces.bbystatic.com) - works for electronics
   - Amazon CDN (m.media-amazon.com) - works for most products
   - Manufacturer websites - for kitchen appliances, tools, etc.
   - Walmart, Target, Home Depot CDNs as backup
4. Research problems/complaints for EACH product (Reddit, forums, Amazon reviews)
5. Write a comprehensive comparison post with:
   - Quick verdict table at top
   - Individual product sections with honest pros/cons
   - Head-to-head comparison table
   - 'How to Choose' decision guide
   - FAQ section
6. Use affiliate tag: amazonfi08e0c-20 for ALL Amazon links
7. Assign the correct category (Kitchen Appliances, Electronics, Home & Garden, etc.)
8. Commit and push to main branch

CRITICAL:
- All affiliate links MUST use tag=amazonfi08e0c-20
- Download at least 1 image per product (3 minimum total)
- Include real cons/downsides for each product - builds trust"

    log "Running Claude Code..."

    # Run Claude Code
    $CLAUDE_PATH --print -p "$PROMPT" \
        --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch,Grep,Glob" \
        2>&1 | tee -a "$LOG_FILE"

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        log "SUCCESS: Blog post created for '$TOPIC'"
        mark_completed "$TOPIC"
    else
        log "ERROR: Failed to create blog post (exit code: $EXIT_CODE)"
    fi

    log "Finished at $(date)"
    log "========================================="
}

# Run main function
main
