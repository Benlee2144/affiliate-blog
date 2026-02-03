# Claude Instructions for Amazon Affiliate Blog

## Project Overview
This is an Amazon affiliate blog built with Hugo, deployed on GitHub Pages at:
**https://benlee2144.github.io/affiliate-blog/**

Owner: Benjamin Arp

## Quick Start: Creating a New Blog Post

When the user provides an Amazon affiliate link:

1. **Extract the ASIN** from the URL (e.g., `B09V3KXJPB` from `amazon.com/dp/B09V3KXJPB`)
2. **Research the product** using WebSearch:
   - Search: "[Product name] review Reddit"
   - Search: "[Product name] problems complaints"
   - Search: "[Product name] vs [competitor]"
3. **Download 5 product images** from Amazon to `/static/images/products/`
4. **Write the blog post** following Wirecutter style (see below)
5. **Save to** `/content/posts/[product-slug].md`
6. **Build and verify**: `hugo --gc --minify`
7. **ALWAYS verify the live site** after pushing - check homepage card images display correctly
8. **Commit and push** to GitHub

## Critical Path Rules

- **Image paths MUST include `/affiliate-blog/` prefix** (site is in subdirectory)
  - Correct: `/affiliate-blog/images/products/product-1.jpg`
  - Wrong: `/images/products/product-1.jpg`

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
| Outdoor | Camping, hiking, recreation | 🏕️ |

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
6. **Honest Downsides** - Real cons from owner feedback
7. **Who Should Buy** - Specific use cases
8. **Competition Comparison** - Table with 2-3 alternatives
9. **Product Gallery** - Multiple images throughout
10. **Bottom Line** - Final recommendation with CTA
11. **FAQ Section** - In front matter for schema

### Writing Rules:

- **Specific over vague**: "1000W motor" not "powerful motor"
- **Cite sources**: "Multiple r/Blenders users report..."
- **Include cons**: Every product has weaknesses - builds trust
- **Unique summaries**: Never use the same opening pattern twice
- **No fluff**: Cut "In this article" and "Let's dive in"

### Front Matter Template:

```yaml
---
title: "[Product] Review (2026): [Compelling Hook]"
date: 2026-XX-XXT10:30:00+00:00
lastmod: 2026-XX-XXT10:30:00+00:00
draft: false
description: "After analyzing X+ owner reviews and Reddit discussions, here's whether the [Product] is worth buying—and [unique angle]."
summary: "[Unique, clickable summary - different for every post]"

keywords: ["[product] review", "[product] vs [competitor]", "best [category] 2026"]

categories: ["[Category from list above]"]
tags: ["[Brand]", "[category]", "product review", "buying guide"]

review: true
product_name: "[Full Product Name]"
product_image: "/affiliate-blog/images/products/[slug]-1.jpg"
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
    image: "/affiliate-blog/images/products/[slug]-1.jpg"
    alt: "[Product name]"
    caption: "Our top pick for [use case]"
    relative: false
---
```

## Shortcodes Available

```hugo
{{< cta-button url="https://amazon.com/dp/ASIN?tag=amazonfi08e0c-20" text="Check Price on Amazon" >}}

{{< related-post slug="other-post-slug" text="our review of X" >}}
```

## Pre-Push Checklist

Before pushing any changes:

- [ ] Hugo build succeeds: `hugo --gc --minify`
- [ ] Images display correctly (check paths have `/affiliate-blog/` prefix)
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
- [ ] FAQ section appears at bottom of post

## File Locations

```
/content/posts/          - Blog posts
/static/images/products/ - Product images
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
- Schema.org (Product, Review, FAQ, BreadcrumbList, Organization, WebSite)
- Open Graph & Twitter Cards
- Canonical URLs
- Sitemap generation
- robots.txt
- About page with E-E-A-T content

User needs to set up:
- Google Search Console (submit sitemap)
- Google Analytics (add GA4 ID to config.toml)

## Common Issues & Fixes

**Images not showing**: Check path has `/affiliate-blog/` prefix

**Homepage card image too zoomed/cropped**: Image uses `object-fit: cover` with 16:10 aspect ratio. Use product images that work well cropped to landscape.

**Build fails on "shortcode not found"**: Create the shortcode in `/themes/papermod-custom/layouts/shortcodes/`

**Tables look cramped**: CSS is in `/themes/papermod-custom/layouts/partials/css/style.css`

**GitHub Action fails**: Check the error in the Actions tab on GitHub

## Design Guidelines

- Keep white/clean aesthetic
- Professional icons only (no childish emojis)
- Trust signals: Deep Research, Honest Takes, Clear Guidance
- Category colors are pre-defined in terms.html
