# Auto Blog Generator for Researched Picks

Automatically generates "Best 3" comparison blog posts using Claude Code.

## Setup Instructions (Mac)

### 1. Make the script executable
```bash
chmod +x /home/user/affiliate-blog/automation/auto-blog.sh
```

### 2. Update the Claude path (if needed)
Edit `auto-blog.sh` and update `CLAUDE_PATH` to match your Claude Code installation:
```bash
CLAUDE_PATH="/usr/local/bin/claude"  # or wherever claude is installed
```

Find your claude path with: `which claude`

### 3. Set up the cron job with randomized timing

Open crontab:
```bash
crontab -e
```

Add this line to run every 4-6 hours with built-in randomization:
```bash
# Run at varied times: 2am, 7am, 1pm, 6pm, 11pm (with random delays built into script)
0 2,7,13,18,23 * * * /home/user/affiliate-blog/automation/auto-blog.sh
```

Or for testing, run every hour:
```bash
0 * * * * /home/user/affiliate-blog/automation/auto-blog.sh
```

### 4. Keep your Mac awake (optional but recommended)

Install `caffeinate` wrapper or use:
```bash
# Prevent sleep while script runs
caffeinate -i /home/user/affiliate-blog/automation/auto-blog.sh
```

Or in System Preferences → Energy Saver → Prevent computer from sleeping automatically

## How It Works

1. **Random topic selection** - Picks randomly from unused topics (not sequential)
2. **Random delays** - Adds 0-90 minute random delay before posting
3. **Varied posting times** - Cron runs at irregular hours (not every 5 hours exactly)
4. **Topic tracking** - Marks topics as done with `# [DONE]` prefix
5. **Logging** - All activity logged to `blog.log`

## Files

- `topics.txt` - Queue of blog topics (add more anytime)
- `auto-blog.sh` - Main automation script
- `blog.log` - Activity log

## Managing Topics

**Add new topics:**
Just add lines to `topics.txt` (one topic per line)

**View completed topics:**
```bash
grep "DONE" topics.txt
```

**View remaining topics:**
```bash
grep -v "^#" topics.txt | grep -v "^$"
```

**Reset all topics:**
Remove the `# [DONE]` prefix from lines you want to reuse

## Troubleshooting

**Check logs:**
```bash
tail -100 /home/user/affiliate-blog/automation/blog.log
```

**Test manually:**
```bash
/home/user/affiliate-blog/automation/auto-blog.sh
```

**Check cron is running:**
```bash
crontab -l
```

## Cost Estimate

Each blog post uses approximately:
- ~50-100k tokens input
- ~10-20k tokens output
- Estimated cost: $0.50-2.00 per post

At 4-5 posts per day: ~$2-10/day or $60-300/month
