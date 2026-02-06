# Claude Instructions for Researched Picks

## Project Overview
This is an Amazon affiliate blog built with Hugo, deployed on GitHub Pages with custom domain:
**https://researchedpick.com/**

Site Name: **Researched Picks**
Owner: Ben Arp

## Quick Start: Creating a New Blog Post

When the user provides an Amazon affiliate link:

1. **Extract the ASIN** from the URL (e.g., `B09V3KXJPB` from `amazon.com/dp/B09V3KXJPB`)
2. **Research the product thoroughly** using WebSearch (ALL THREE REQUIRED):
   - Search: "[Product name] review Reddit" - Find real user experiences
   - Search: "[Product name] problems complaints issues" - Discover honest downsides
   - Search: "[Product name] vs [competitor]" - Understand the competition
3. **Download AT LEAST 3 product images** to `/static/images/products/`
   - Sources: Apple Newsroom, manufacturer press kits, Best Buy, Newegg, Amazon CDN
   - Name them: `[product-slug]-1.jpg`, `[product-slug]-2.jpg`, `[product-slug]-3.jpg`
4. **Find a YouTube video review** of the product
   - Search: "[Product name] review" on YouTube
   - Pick a high-quality, informative review (good audio, thorough coverage)
   - Extract the video ID from the URL (e.g., `dQw4w9WgXcQ` from `youtube.com/watch?v=dQw4w9WgXcQ`)
5. **Write the blog post** following Wirecutter style (see below)
6. **Save to** `/content/posts/[product-slug].md`
7. **Build and verify**: `hugo --gc --minify`
8. **ALWAYS verify the live site** after pushing - check homepage card images display correctly
9. **Commit and push** to GitHub

## CRITICAL REQUIREMENTS (Never Skip These)

1. **MINIMUM 3 IMAGES per blog post** - Every review MUST have at least 3 product images scattered throughout the content. This is non-negotiable.

2. **YOUTUBE VIDEO per blog post** - Every review MUST include an embedded YouTube video review of the product. Search for "[Product name] review" on YouTube and embed a high-quality review video using the shortcode: `{{</* youtube VIDEO_ID */>}}`

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

## Git Workflow

```bash
cd "/Users/benjaminarp/Desktop/amazon website/affiliate-blog"
hugo --gc --minify
git add .
git commit -m "Add [product] review"
git push origin main
```

Site rebuilds automatically via GitHub Actions after push.

## SEO Setup Status

Done:
- Custom domain: researchedpick.com
- Schema.org (Product, Review, FAQ, BreadcrumbList, Organization, WebSite)
- Open Graph & Twitter Cards
- Canonical URLs
- Sitemap generation (https://researchedpick.com/sitemap.xml)
- robots.txt
- About page with E-E-A-T content

User needs to set up:
- Google Search Console (submit sitemap: https://researchedpick.com/sitemap.xml)
- Google Analytics (add GA4 ID to config.toml)
- Connect domain DNS to GitHub Pages (see instructions below)

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

## How to Download Amazon Product Images

Amazon CDN images can be downloaded directly without blocking. Use this approach:

**Step 1: Find Image IDs**
- Search: `"[Product Name] amazon" site:m.media-amazon.com`
- Or search: `[Product Name] ASIN [asin-code] amazon images`
- Look for image IDs like `71LB1AbsorL` or `61Eu-FwDfZL`

**Step 2: Construct CDN URLs**
Format: `https://m.media-amazon.com/images/I/[IMAGE_ID]._AC_SL1500_.jpg`

Example for image ID `71LB1AbsorL`:
```
https://m.media-amazon.com/images/I/71LB1AbsorL._AC_SL1500_.jpg
```

**Step 3: Download with curl**
```bash
curl -L -A "Mozilla/5.0" -o product-1.jpg "https://m.media-amazon.com/images/I/[ID]._AC_SL1500_.jpg"
```

**Image size variants:**
- `_AC_SL1500_` = 1500px (high res, best for blogs)
- `_AC_SL1000_` = 1000px
- `_AC_SL500_` = 500px (smaller file)

**Alternative sources if Amazon blocks:**
1. Manufacturer website (check their CDN - Shopify stores use `cdn.shopify.com`)
2. Best Buy: `pisces.bbystatic.com`
3. Micro Center: `productimages.microcenter.com`

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

## Design Guidelines

- Site name: "Researched Picks"
- Tagline: "Honest Reviews. Real Research."
- Keep white/clean aesthetic
- Professional icons only (no childish emojis)
- Trust signals: Deep Research, Honest Takes, Clear Guidance
- Category colors are pre-defined in terms.html
