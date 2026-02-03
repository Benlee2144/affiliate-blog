# Amazon Affiliate Blog System

A complete Hugo-based affiliate blog with automated blog post generation. Paste an Amazon link, get a researched, SEO-optimized review ready to publish.

## Quick Start

```bash
# 1. Install Hugo (macOS)
brew install hugo

# 2. Install Python dependencies
cd scripts
pip install -r requirements.txt

# 3. Generate a blog post
python generate_post.py "https://www.amazon.com/dp/B08N5WRWNW?tag=amazonfi08e0c-20"

# 4. Preview locally
cd ..
hugo server -D

# 5. Open http://localhost:1313
```

## Project Structure

```
affiliate-blog/
├── archetypes/          # Post templates
├── content/
│   ├── posts/           # Blog posts go here
│   └── pages/           # Static pages (about, privacy, etc.)
├── layouts/             # Custom layout overrides
├── static/
│   └── images/
│       └── products/    # Downloaded product images
├── themes/
│   └── papermod-custom/ # Custom theme
├── scripts/
│   ├── generate_post.py # Blog post generator
│   └── requirements.txt
├── config.toml          # Hugo configuration
└── README.md
```

## Installation

### 1. Install Hugo

**macOS (Homebrew):**
```bash
brew install hugo
```

**Windows (Chocolatey):**
```bash
choco install hugo-extended
```

**Linux (Snap):**
```bash
snap install hugo
```

Verify installation:
```bash
hugo version
```

### 2. Install Python Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `python-slugify` - URL-safe slugs

### 3. Configure Your Site

Edit `config.toml`:

```toml
baseURL = "https://yourusername.github.io/affiliate-blog/"
title = "Your Site Name"

[params]
  author = "Your Name"
  description = "Your site description"
```

## Using the Blog Post Generator

### Basic Usage

```bash
python scripts/generate_post.py "AMAZON_PRODUCT_URL"
```

### What It Does

1. **Extracts product info** from Amazon (title, price, rating, features)
2. **Downloads product images** to `static/images/products/`
3. **Generates a complete blog post** with:
   - SEO-optimized title and meta description
   - Proper front matter with schema markup
   - Product showcase box with affiliate link
   - Pros/cons section (with placeholders for research)
   - Competitor comparison table
   - FAQ section targeting long-tail keywords
   - Proper `rel="nofollow sponsored"` on affiliate links

### Options

```bash
# Skip downloading images
python generate_post.py --no-images "https://amazon.com/dp/..."

# Custom output directory
python generate_post.py --output-dir /path/to/posts "https://amazon.com/dp/..."
```

### After Generation

The script creates a draft post with `[RESEARCH]` placeholders. You need to:

1. **Fill in research placeholders** with actual findings from:
   - Reddit discussions (search: "productname reddit review")
   - YouTube reviews (especially long-term owner feedback)
   - Amazon verified purchase reviews (sort by "most recent")
   - Niche forums for the product category

2. **Review and edit** the content for your voice

3. **Remove `draft: true`** when ready to publish

## Local Development

### Preview Your Site

```bash
hugo server -D
```

- Site available at `http://localhost:1313`
- `-D` flag shows draft posts
- Live reload on file changes

### Build for Production

```bash
hugo --minify
```

Output goes to `public/` directory.

## Deploying to GitHub Pages

### Method 1: GitHub Actions (Recommended)

1. Create `.github/workflows/hugo.yml`:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      HUGO_VERSION: 0.121.0
    steps:
      - name: Install Hugo CLI
        run: |
          wget -O ${{ runner.temp }}/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb \
          && sudo dpkg -i ${{ runner.temp }}/hugo.deb
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4
      - name: Build with Hugo
        env:
          HUGO_ENVIRONMENT: production
          HUGO_ENV: production
        run: |
          hugo \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v3
```

2. In GitHub repo settings:
   - Go to Settings → Pages
   - Source: "GitHub Actions"

3. Push to main branch to deploy

### Method 2: Manual Deploy

```bash
# Build site
hugo --minify

# The public/ folder contains your site
# Upload contents to your hosting
```

## Adding a Custom Domain

1. Add your domain in GitHub repo Settings → Pages → Custom domain

2. Create `static/CNAME` file with your domain:
```
www.yourdomain.com
```

3. Update `config.toml`:
```toml
baseURL = "https://www.yourdomain.com/"
```

4. Configure DNS:
   - A records pointing to GitHub's IPs
   - Or CNAME record pointing to `yourusername.github.io`

## Adding Google AdSense

When approved, add your AdSense code:

1. Edit `themes/papermod-custom/layouts/_default/baseof.html`

2. Find the AdSense placeholder comment and replace:

```html
<!-- AdSense Placeholder - Add your AdSense code here when approved -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX" crossorigin="anonymous"></script>
```

3. Ad placements are already set up in templates. Uncomment them:
   - Before content in `single.html`
   - After content in `single.html`
   - In listing pages in `list.html`

## Adding Google Analytics

1. Get your GA4 Measurement ID (G-XXXXXXXXXX)

2. Edit `config.toml`:
```toml
[params.analytics]
  google = "G-XXXXXXXXXX"
```

## Creating Posts Manually

If you prefer not to use the generator:

```bash
hugo new posts/my-product-review.md
```

Then edit the file with proper front matter. See `archetypes/default.md` for the template.

## Content Guidelines

### Anti-AI-Slop Rules

The generator avoids these phrases, and you should too:

**Never use:**
- "In today's world..."
- "Whether you're a... or a..."
- "Let's dive in" / "Let's explore"
- "Game-changer"
- "Take it to the next level"
- "Unlock" / "Unleash"
- "Seamless" / "Robust"

**Instead:**
- Be conversational but not fake-friendly
- Use contractions (don't, won't, it's)
- Have actual opinions
- Be specific with numbers and specs
- Admit negatives upfront
- Sound like you've actually researched it

### SEO Structure

- Primary keyword in first 100 words
- H2s that match search queries ("Is X worth it?")
- Short paragraphs (2-3 sentences)
- FAQ section with "People Also Ask" questions
- Specific numbers: dimensions, wattage, price

### Compliance

Every post automatically includes:
- Affiliate disclosure at top
- `rel="nofollow sponsored"` on affiliate links
- Schema markup for products and reviews

## Shortcodes

### Product Box
```markdown
{{< product-box
    name="Product Name"
    image="/images/products/product.jpg"
    price="$XX.XX"
    link="https://amazon.com/..."
    rating="4.5"
>}}
```

### Pros and Cons
```markdown
{{< pros-cons >}}
PROS:
- Pro item 1
- Pro item 2

CONS:
- Con item 1
- Con item 2
{{< /pros-cons >}}
```

### Affiliate Link Button
```markdown
{{< affiliate-link url="https://amazon.com/..." text="Check Price on Amazon" >}}
```

### Comparison Table
```markdown
{{< comparison-table >}}
| Feature | Product A | Product B |
|---------|-----------|-----------|
| Price | $50 | $75 |
| Power | 500W | 700W |
{{< /comparison-table >}}
```

## Troubleshooting

### Generator can't fetch Amazon page

Amazon sometimes blocks scraping. Try:
- Wait a few minutes and retry
- Use a VPN
- Use `--no-images` flag and add images manually

### Hugo build errors

```bash
# Check for syntax errors
hugo --verbose

# Common issues:
# - Unclosed shortcodes
# - Invalid YAML in front matter
# - Missing closing brackets
```

### Images not showing

- Check paths start with `/images/products/`
- Verify files exist in `static/images/products/`
- Clear browser cache

## File Checklist

Before publishing, verify:

- [ ] `draft: false` in front matter
- [ ] All `[RESEARCH]` placeholders replaced
- [ ] Product images downloaded and referenced correctly
- [ ] Affiliate link has your tag
- [ ] Meta description under 160 characters
- [ ] No banned AI phrases

## Support

For Hugo documentation: https://gohugo.io/documentation/

For issues with this template: [your-email@example.com]
