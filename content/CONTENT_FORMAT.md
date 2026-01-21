# Content File Format Guide

This guide explains how to structure your content files for the Camp Lakota WordPress Publisher.

---

## File Structure

Place your content files in the appropriate directories:
```
content/
├── pages/          # Landing pages (*.json files)
├── posts/          # Blog posts (*.json files)
└── images/         # All images referenced in your content
```

---

## Page Format (JSON)

### Required Fields
- `title` - Page title
- `content` - HTML content of the page

### Optional Fields
- `slug` - URL slug (auto-generated from title if not provided)
- `status` - "publish" (default), "draft", "pending", "private"
- `excerpt` - Short summary
- `meta_title` - SEO title
- `meta_description` - SEO description
- `featured_image` - Filename of featured image (must be in content/images/)
- `featured_image_alt` - Alt text for featured image
- `meta` - Custom meta fields (depends on your WP setup)

### Example: landing-page.json
```json
{
  "title": "Summer Camp Programs",
  "slug": "summer-camp-programs",
  "content": "<h2>Our Programs</h2><p>Discover amazing summer activities...</p>",
  "status": "publish",
  "meta_title": "Summer Camp Programs - Camp Lakota",
  "meta_description": "Explore our diverse summer camp programs designed for kids of all ages.",
  "featured_image": "summer-programs-hero.jpg",
  "featured_image_alt": "Children participating in summer camp activities"
}
```

---

## Post Format (JSON)

### Required Fields
- `title` - Post title
- `content` - HTML content of the post

### Optional Fields
- `slug` - URL slug (auto-generated from title if not provided)
- `status` - "publish" (default), "draft", "pending", "private"
- `excerpt` - Short summary/preview
- `meta_title` - SEO title
- `meta_description` - SEO description
- `categories` - Array of category IDs (will be created if names provided)
- `tags` - Array of tag IDs (will be created if names provided)
- `featured_image` - Filename of featured image
- `featured_image_alt` - Alt text for featured image
- `author` - Author ID (uses authenticated user if not provided)
- `author_name` - Author name for schema
- `date` - Publish date in ISO format (YYYY-MM-DDTHH:MM:SS)

### Example: top-10-activities.json
```json
{
  "title": "Top 10 Summer Camp Activities",
  "slug": "top-10-summer-camp-activities",
  "content": "<h2>Activities Your Kids Will Love</h2><p>From swimming to archery...</p>",
  "excerpt": "Discover the top 10 activities that make our camp special",
  "status": "publish",
  "meta_title": "Top 10 Camp Activities - Camp Lakota Blog",
  "meta_description": "Discover the top 10 activities at Camp Lakota that kids love most.",
  "categories": ["Summer Camp", "Activities"],
  "tags": ["outdoor activities", "kids", "summer"],
  "featured_image": "activities-collage.jpg",
  "featured_image_alt": "Collage of summer camp activities",
  "author_name": "Sarah Johnson",
  "date": "2026-01-15T09:00:00"
}
```

---

## Internal Linking

Use placeholders in your content to reference other pages/posts:

### Format
```
{{link:slug}}                           → Full URL
{{link:slug|anchor text}}               → Full HTML link
```

### Examples
```html
<!-- In your content -->
<p>Learn more about {{link:summer-camp-programs|our programs}}.</p>

<!-- After publishing, becomes -->
<p>Learn more about <a href="https://yoursite.com/summer-camp-programs">our programs</a>.</p>
```

**Important:** Internal links are processed AFTER all content is published, so the slugs must match exactly.

---

## Images

### Image Files
- Place all images in `content/images/`
- Supported formats: JPG, PNG, WebP, GIF
- Recommended: Optimize images before adding (< 500KB each)
- Use descriptive filenames: `camp-lakota-swimming-pool.jpg` ✅ not `IMG_1234.jpg` ❌

### Image Metadata
Specify in your content JSON:
```json
{
  "featured_image": "summer-camp-hero.jpg",
  "featured_image_alt": "Children enjoying summer activities at Camp Lakota"
}
```

For multiple images in content, upload separately and reference them in your HTML:
```json
{
  "content": "<img src='{{upload:archery-lesson.jpg}}' alt='Kids learning archery' />"
}
```

---

## SEO & Meta Fields

### Meta Title
- **Length:** 50-60 characters (including site name)
- **Format:** Primary Keyword - Secondary Keyword | Brand
- **Example:** "Summer Camp Programs - Activities & Registration | Camp Lakota"

### Meta Description
- **Length:** 150-160 characters
- **Action-oriented:** Include call to action
- **Example:** "Discover exciting summer camp programs at Camp Lakota. Swimming, hiking, arts & more! Register today for an unforgettable summer."

### Focus Keyword
Optional, for SEO plugins:
```json
{
  "focus_keyword": "summer camp programs"
}
```

---

## Schema Markup

Schema can be added automatically or manually:

### Automatic (Recommended)
The publisher can auto-generate schema. Provide info in your JSON:
```json
{
  "schema_type": "LocalBusiness",
  "business_info": {
    "name": "Camp Lakota",
    "phone": "(555) 123-4567",
    "address": {
      "street": "123 Camp Road",
      "city": "Lake City",
      "state": "CA",
      "zip": "12345"
    }
  }
}
```

### Manual
Include schema directly in your content:
```json
{
  "content": "<script type='application/ld+json'>{ ... schema JSON ... }</script><h2>...</h2>"
}
```

---

## Status Options

- **publish** - Publicly visible immediately
- **draft** - Saved but not public (good for testing)
- **pending** - Awaiting review
- **private** - Only visible to admins

**Tip:** Start with `"status": "draft"` to test, then change to `"status": "publish"` when ready.

---

## Best Practices

### Content Structure
1. **One file per page/post**
2. **Descriptive filenames:** `about-camp-lakota.json` ✅
3. **Valid JSON:** Use a JSON validator before uploading
4. **HTML in content:** Use proper HTML tags

### Images
1. **Optimize first:** Compress images before adding
2. **Descriptive names:** `summer-activities-hero.jpg` ✅
3. **Alt text always:** Important for accessibility and SEO
4. **Size appropriately:** 1200-1920px wide for heroes

### SEO
1. **Unique meta per page:** Don't duplicate meta descriptions
2. **Include keywords:** Naturally in title and description
3. **Call to action:** In meta descriptions
4. **Length limits:** Titles 50-60 chars, descriptions 150-160 chars

### Internal Linking
1. **Plan ahead:** Map which pages link to which
2. **Natural anchor text:** Use descriptive link text
3. **Check slugs:** Must match exactly (case-sensitive)

---

## Validation Checklist

Before publishing, verify:
- [ ] All JSON files are valid (use JSONLint.com)
- [ ] Required fields present (title, content)
- [ ] Image files exist in content/images/
- [ ] Slugs are lowercase with hyphens only
- [ ] Meta descriptions under 160 characters
- [ ] Internal link slugs match actual file slugs
- [ ] Status set correctly (draft vs publish)

---

## Example: Complete Page

```json
{
  "title": "About Camp Lakota",
  "slug": "about-camp-lakota",
  "status": "publish",
  "content": "<h2>Welcome to Camp Lakota</h2>\n<p>Since 1985, Camp Lakota has been providing unforgettable summer experiences...</p>\n<p>{{link:summer-camp-programs|Explore our programs}} or {{link:contact|get in touch}} today!</p>",
  "excerpt": "Learn about Camp Lakota's 40-year history of creating magical summer memories",
  "meta_title": "About Camp Lakota - Summer Camp Since 1985",
  "meta_description": "Discover Camp Lakota's rich history and commitment to providing safe, fun, and educational summer experiences for children of all ages.",
  "featured_image": "about-camp-hero.jpg",
  "featured_image_alt": "Historic photo of Camp Lakota's main lodge",
  "schema_type": "Organization",
  "business_info": {
    "name": "Camp Lakota",
    "description": "Premier summer camp for children ages 6-16",
    "url": "https://camplakota.com"
  }
}
```

---

## Need Help?

- **JSON Validation:** https://jsonlint.com
- **Schema Testing:** https://search.google.com/test/rich-results
- **Image Optimization:** TinyPNG.com or ImageOptim
- **HTML Reference:** https://developer.mozilla.org/en-US/docs/Web/HTML

---

**Ready to create your content?** Follow this format, and the publisher will handle the rest! 🏕️
