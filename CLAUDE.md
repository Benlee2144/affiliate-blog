# Claude Instructions for Researched Picks

## Project Overview
This is an Amazon affiliate blog built with Hugo, deployed on GitHub Pages with custom domain:
**https://researchedpick.com/**

Site Name: **Researched Picks**
Owner: Ben Arp
Contact: benarp2144@gmail.com

## Quick Start: Creating a New Blog Post

### Single Product Review
When the user provides an Amazon affiliate link:

1. **Extract the ASIN** from the URL (e.g., `B09V3KXJPB` from `amazon.com/dp/B09V3KXJPB`)
2. **Research the product thoroughly** using WebSearch (ALL THREE REQUIRED):
   - Search: "[Product name] review Reddit" - Find real user experiences
   - Search: "[Product name] problems complaints issues" - Discover honest downsides
   - Search: "[Product name] vs [competitor]" - Understand the competition
3. **Download AT LEAST 3 product images** to `/static/images/products/`
   - Sources: Apple Newsroom, manufacturer press kits, Best Buy, Newegg, Amazon CDN
   - Name them: `[product-slug]-1.jpg`, `[product-slug]-2.jpg`, `[product-slug]-3.jpg`
4. **Find a YouTube video review** of the product (if one exists)
   - Search: "[Product name] review" on YouTube
   - ONLY use a video that reviews the EXACT same product (same model number)
   - Do NOT use random or unrelated videos - skip this step if no matching video exists
   - Extract the video ID from the URL (e.g., `dQw4w9WgXcQ` from `youtube.com/watch?v=dQw4w9WgXcQ`)
5. **Write the blog post** following Wirecutter style (see below)
6. **Save to** `/content/posts/[product-slug].md`
7. **Build and verify**: `hugo --gc --minify`
8. **ALWAYS verify the live site** after pushing - check homepage card images display correctly
9. **Commit and push** to GitHub

### Comparison Blog Posts (Best X for Y 2026)
When user asks for a "best of" comparison post:

1. **Research the category** - Find top 3 products that fit different use cases/budgets
2. **Find Amazon ASINs** for all 3 products
3. **Download 1 image per product minimum** (3 total) from Best Buy CDN
4. **Research problems/complaints** for EACH product individually
5. **Write comparison post** with:
   - Quick verdict table at top
   - Individual sections for each product with pros/cons
   - Head-to-head comparison table
   - "How to Choose" decision guide
   - YouTube video if available
6. **All 3 products must have affiliate links** with tag `amazonfi08e0c-20`

Example posts created:
- Best Cameras for Content Creators 2026
- Best Microphones for Content Creators 2026
- Best Laptops for Coding 2026
- Best iPads for College Students 2026

## CRITICAL REQUIREMENTS (Never Skip These)

1. **MINIMUM 3 IMAGES per blog post** - Every review MUST have at least 3 product images scattered throughout the content. This is non-negotiable.

2. **YOUTUBE VIDEO per blog post (if available)** - Search for "[Product name] review" on YouTube. ONLY embed a video if it's an actual review of the EXACT product (same model number). Do NOT embed random or unrelated videos. If no matching video exists, skip this section entirely. Use shortcode: `{{</* youtube VIDEO_ID */>}}`

3. **THOROUGH RESEARCH** - Every review MUST include research from:
   - Reddit discussions (real user feedback)
   - Problems/complaints searches (honest downsides)
   - Competitor comparisons (context for readers)

4. **CITE YOUR SOURCES** - Include quotes from Reddit users, forum posts, or verified reviews in the article to build trust.

## Critical Path Rules

- **Image paths**: Use `/images/products/product-1.jpg` (NO prefix needed - custom domain)
- **Affiliate tag**: `amazonfi08e0c-20`
  - Link format: `https://www.amazon.com/dp/[ASIN]?tag=amazonfi08e0c-20`

- **ALWAYS CHECK THE LIVE SITE** after every new blog post to verify:
  - Homepage card shows product image correctly
  - Review page images all load
  - Category page displays the new post

## Categories (Pre-Styled with Professional Icons)

Always assign posts to the correct category:

| Category | Products | Icon |
|----------|----------|------|
| Tablets | iPads, Android tablets, e-readers | 📱 |
| Kitchen Appliances | Blenders, air fryers, coffee makers, instant pots | ⚡ |
| Electronics | Gadgets, audio gear, smart devices | 🎧 |
| Home & Garden | Tools, furniture, outdoor gear | 🏠 |
| Fitness | Exercise equipment, fitness trackers | 💪 |
| Beauty | Skincare, haircare, beauty tools | ✨ |
| Office | Desks, chairs, productivity tools | 💼 |
| Outdoor | Camping, hiking, recreation | ⛰️ |

**Professional Icons to Use** (avoid childish emojis):
- Trust/Quality: ✓ ★ ◆
- Categories: Use icons above
- Avoid: 🎉 🤪 😍 💕 or overly casual emojis

## Wirecutter-Style Writing Guide

### Structure Every Post Must Have:

1. **Affiliate Disclosure** (first line after front matter)
2. **Pain Point Opening** - Start with the reader's frustration
3. **Bold Verdict** - "Our verdict: [Product] is the best [category] for [use case]"
4. **Our Pick Section** with:
   - Product image
   - Quick take (one compelling benefit)
   - "Best for:" and "Skip if:" bullets
   - CTA button
5. **Why It Stands Out** - Specific pros with sources (Reddit, Amazon reviews)
6. **YouTube Video Review** - Embed a video review using `{{</* youtube VIDEO_ID */>}}` with intro text like "See it in action:"
7. **Honest Downsides** - Real cons from owner feedback
8. **Who Should Buy** - Specific use cases
9. **Competition Comparison** - Table with 2-3 alternatives
10. **Product Gallery** - Multiple images throughout
11. **Bottom Line** - Final recommendation with CTA
12. **FAQ Section** - In front matter for schema

### Writing Rules:

- **Specific over vague**: "1000W motor" not "powerful motor"
- **Cite sources**: "Multiple r/Blenders users report..."
- **Include cons**: Every product has weaknesses - builds trust
- **Unique summaries**: Never use the same opening pattern twice
- **No fluff**: Cut "In this article" and "Let's dive in"

### Front Matter Template:

**IMPORTANT DATE RULE**: Always use a **past time** for the date field! Hugo's `buildFuture = false` means posts with future dates won't build. Use today's date with a time that has already passed (e.g., if it's 3pm, use `T10:00:00`).

```yaml
---
title: "[Product] Review (2026): [Compelling Hook]"
date: 2026-XX-XXT00:00:00+00:00  # USE PAST TIME - midnight UTC is safe
lastmod: 2026-XX-XXT00:00:00+00:00
draft: false
description: "After analyzing X+ owner reviews and Reddit discussions, here's whether the [Product] is worth buying—and [unique angle]."
summary: "[Unique, clickable summary - different for every post]"

keywords: ["[product] review", "[product] vs [competitor]", "best [category] 2026"]

categories: ["[Category from list above]"]
tags: ["[Brand]", "[category]", "product review", "buying guide"]

review: true
product_name: "[Full Product Name]"
product_image: "/images/products/[slug]-1.jpg"
brand: "[Brand]"
rating: [4.X]
price: "$XX.XX"
affiliate_link: "https://www.amazon.com/dp/[ASIN]?tag=amazonfi08e0c-20"
asin: "[ASIN]"

author: "Benjamin Arp"
showToc: true
TocOpen: true

faq:
  - question: "Is the [Product] worth the money?"
    answer: "[Direct answer based on research]"
  - question: "[Common question from Google PAA]"
    answer: "[Direct answer]"

cover:
    image: "/images/products/[slug]-1.jpg"
    alt: "[Product name]"
    caption: "Our top pick for [use case]"
    relative: false
---
```

## Shortcodes Available

```hugo
{{< cta-button url="https://amazon.com/dp/ASIN?tag=amazonfi08e0c-20" text="Check Price on Amazon" >}}

{{< youtube VIDEO_ID >}}  <!-- Embeds a YouTube video - VIDEO_ID is from the URL after v= -->

{{< related-post slug="other-post-slug" text="our review of X" >}}
```

## Pre-Push Checklist

Before pushing any changes:

- [ ] Hugo build succeeds: `hugo --gc --minify`
- [ ] **Page count increased** (new post should add pages - if not, check date!)
- [ ] Images display correctly (paths start with `/images/`)
- [ ] YouTube video embedded with valid video ID
- [ ] Tables have proper spacing (not "ran together")
- [ ] Summary is unique (not repetitive pattern)
- [ ] Category is correct for product type
- [ ] All affiliate links have correct tag

## Post-Push Checklist (ALWAYS DO THIS)

After pushing a new blog post, verify on the live site:

- [ ] Homepage shows new post card with image
- [ ] Product image displays correctly on homepage card (not too zoomed)
- [ ] Category page lists the new post
- [ ] Individual review page loads all images
- [ ] YouTube video plays correctly
- [ ] FAQ section appears at bottom of post

## File Locations

```
/content/posts/          - Blog posts
/static/images/products/ - Product images
/static/CNAME           - Custom domain config
/themes/papermod-custom/ - Theme files
/config.toml            - Site configuration
```

### Favicon Files (in /static/)
- `favicon.ico` - Multi-size ICO (48, 32, 16px)
- `favicon-192x192.png` - For Google search results & Android
- `favicon-32x32.png` - Browser tabs
- `favicon-16x16.png` - Small browser tabs
- `apple-touch-icon.png` - iOS home screen (180x180)

## Git Workflow

```bash
hugo --gc --minify
git add .
git commit -m "Add [product] review"
git push origin main
```

Site rebuilds automatically via GitHub Actions after push.

**IMPORTANT**: The live site deploys from the `main` branch only. If working on a feature branch, you MUST merge to main for changes to appear on the live site:

```bash
git checkout main
git pull origin main
git merge [feature-branch]
git push origin main
```

## SEO Setup Status

Done:
- Custom domain: researchedpick.com
- Schema.org (Product, Review, FAQ, BreadcrumbList, Organization, WebSite)
- Open Graph & Twitter Cards
- Canonical URLs
- Sitemap generation (https://researchedpick.com/sitemap.xml)
- robots.txt
- About page with E-E-A-T content
- Google Search Console (verified)
- Google Analytics (GA4 connected)
- Professional favicon set (RP logo) for Google search results
- DNS configured for GitHub Pages

## Domain Setup (GitHub Pages)

1. Go to your domain registrar (where you bought researchedpick.com)
2. Add these DNS records:
   - Type: A, Host: @, Value: 185.199.108.153
   - Type: A, Host: @, Value: 185.199.109.153
   - Type: A, Host: @, Value: 185.199.110.153
   - Type: A, Host: @, Value: 185.199.111.153
   - Type: CNAME, Host: www, Value: benlee2144.github.io
3. In GitHub repo Settings → Pages → Custom domain: enter "researchedpick.com"
4. Check "Enforce HTTPS" once DNS propagates (can take up to 24 hours)

## How to Download Product Images

### Best Buy CDN (PREFERRED - Most Reliable)
Best Buy images download consistently without blocking.

**Step 1: Find the SKU**
- Search: `[Product Name] Best Buy SKU`
- SKU is a 7-digit number (e.g., `6589380`)

**Step 2: Construct URL and Download**
```bash
curl -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -o /home/user/affiliate-blog/static/images/products/[product-slug]-1.jpg \
  "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/[first4]/[SKU]_sd.jpg"
```

Example for SKU `6589380`:
```bash
curl -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -o product-1.jpg \
  "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6589/6589380_sd.jpg"
```

### Amazon CDN (Backup Option)
Sometimes blocked, but worth trying:

**Step 1: Find Image IDs**
- Search: `"[Product Name] amazon" site:m.media-amazon.com`
- Look for image IDs like `71LB1AbsorL` or `61Eu-FwDfZL`

**Step 2: Download**
```bash
curl -L -A "Mozilla/5.0" -o product-1.jpg "https://m.media-amazon.com/images/I/[ID]._AC_SL1500_.jpg"
```

**Image size variants:**
- `_AC_SL1500_` = 1500px (high res, best for blogs)
- `_AC_SL1000_` = 1000px
- `_AC_SL500_` = 500px (smaller file)

### Other Sources
- Manufacturer press kits/newsrooms
- Newegg, Micro Center CDNs

**Naming convention:** `[product-slug]-1.jpg`, `[product-slug]-2.jpg`, etc.

---

## Common Issues & Fixes

**Post not appearing / 404 error**: The date in front matter is set to a FUTURE time. Hugo won't build posts with `buildFuture = false`. Fix: use `T00:00:00+00:00` (midnight UTC) which is always in the past.

**Images not showing**: Check path starts with `/images/` (no affiliate-blog prefix)

**Homepage card image too zoomed/cropped**: Image uses `object-fit: contain`. Should show full product now.

**Build fails on "shortcode not found"**: Create the shortcode in `/themes/papermod-custom/layouts/shortcodes/`

**Tables look cramped**: CSS is in `/themes/papermod-custom/layouts/partials/css/style.css`

**GitHub Action fails**: Check the error in the Actions tab on GitHub

**Domain not working**: DNS propagation takes up to 24 hours. Verify A records point to GitHub IPs.

**GitHub storage filling up (1GB limit)**: Options:
1. Compress images (resize to 1200px, 80% quality, use WebP)
2. Move images to external CDN (Cloudflare R2, Cloudinary)
3. Switch hosting to Cloudflare Pages (unlimited storage)

## Design Guidelines

- Site name: "Researched Picks"
- Tagline: "Honest Reviews. Real Research."
- Keep white/clean aesthetic
- Professional icons only (no childish emojis)
- Trust signals: Deep Research, Honest Takes, Clear Guidance
- Category colors are pre-defined in terms.html
