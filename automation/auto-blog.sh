#!/bin/bash
# Auto Blog Generator for Researched Picks
# Runs Claude Code to create comparison blog posts with natural timing

# Configuration
BLOG_DIR="/home/user/affiliate-blog"
TOPICS_FILE="$BLOG_DIR/automation/topics.txt"
LOG_FILE="$BLOG_DIR/automation/blog.log"
CLAUDE_PATH="claude"  # Update this if claude is in a different location

# Create log file if it doesn't exist
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
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

    # Get topic
    TOPIC=$(get_random_topic)
    log "Selected topic: $TOPIC"

    # Change to blog directory
    cd "$BLOG_DIR"

    # Create the prompt
    PROMPT="Create a 'Best 3' comparison blog post for: $TOPIC

Follow the CLAUDE.md instructions exactly:
1. Research the category and find the top 3 products
2. Find Amazon ASINs for all 3 products
3. Download product images from Best Buy CDN
4. Research problems/complaints for EACH product
5. Write a comprehensive comparison post with:
   - Quick verdict table
   - Individual product sections with pros/cons
   - Head-to-head comparison table
   - 'How to Choose' decision guide
6. Use affiliate tag: amazonfi08e0c-20
7. Commit and push to main branch

Make sure all affiliate links use tag=amazonfi08e0c-20"

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
