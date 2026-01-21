# Landing Page Design Template
## Based on "Our Story" Page Analysis

**Reference Page:** `/our-story/` (ID: 1292)  
**Last Updated:** January 2026

---

## 🎨 Visual Design Patterns

### 1. Hero Section
**Pattern:**
- Large hero image spanning full width
- Overlay banner in **dark blue** (`#1a3a5c` or similar) with **white text**
- Banner positioned **bottom-right** of hero image
- Banner text: Page title (e.g., "Our Story")

**Implementation:**
```html
<div class="hero-section" style="position: relative;">
  <img src="hero-image.jpg" alt="..." style="width: 100%; height: auto; display: block;">
  <div class="hero-overlay" style="position: absolute; bottom: 20px; right: 20px; background: #1a3a5c; color: white; padding: 1rem 2rem; font-size: 1.5rem; font-weight: bold;">
    Our Story
  </div>
</div>
```

**Key Cues:**
- Hero image: Full width, responsive
- Overlay: Dark blue background, white text, bold
- Position: Bottom-right corner
- Padding: Generous (1rem vertical, 2rem horizontal)

---

### 2. Main Heading
**Pattern:**
- Large, bold heading (`<h2>` or `<h1>`)
- Class: `page-title` or similar
- Positioned immediately after hero
- Clear visual hierarchy

**Implementation:**
```html
<h2 class="page-title" style="font-size: 2.5rem; font-weight: bold; margin-top: 3rem; margin-bottom: 1.5rem; line-height: 1.3;">
  About Camp Lakota
</h2>
```

**Key Cues:**
- Font size: 2.5rem (40px) or larger
- Font weight: Bold
- Top margin: 3rem (spacing from hero)
- Bottom margin: 1.5rem (spacing to content)

---

### 3. Content Paragraphs
**Pattern:**
- Clean, readable paragraphs
- Adequate line spacing (1.7-1.8)
- Bottom margin: 1.5rem
- No excessive padding

**Implementation:**
```html
<p style="margin-bottom: 1.5rem; line-height: 1.7; font-size: 1.05rem;">
  Content text here...
</p>
```

**Key Cues:**
- Line height: 1.7-1.8 for readability
- Bottom margin: 1.5rem between paragraphs
- Font size: 1.05rem (slightly larger than base)

---

### 4. Large Image Blocks
**Pattern:**
- Full-width or near-full-width images
- Max height: 500px (prevents oversized images)
- Padding: `pt-4` (top) and `pb-4` (bottom) = 1rem each
- Centered alignment

**Implementation:**
```html
<div class="large-image-block" style="padding: 1rem 0; margin: 2rem 0;">
  <img src="image.jpg" alt="..." style="width: 100%; max-height: 500px; object-fit: cover; border-radius: 8px; display: block;">
</div>
```

**Key Cues:**
- Max height: 500px
- Padding: 1rem top/bottom (pt-4, pb-4)
- Border radius: 8px for modern look
- Object-fit: cover (maintains aspect ratio)

---

### 5. Side-by-Side Images
**Pattern:**
- Two images displayed horizontally
- Equal width (50% each with gap)
- Responsive: Stack on mobile
- Consistent spacing

**Implementation:**
```html
<div class="side-by-side-images" style="display: flex; gap: 1rem; margin: 2rem 0; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 300px;">
    <img src="left-image.jpg" alt="..." style="width: 100%; height: auto; border-radius: 8px;">
  </div>
  <div style="flex: 1; min-width: 300px;">
    <img src="right-image.jpg" alt="..." style="width: 100%; height: auto; border-radius: 8px;">
  </div>
</div>
```

**Key Cues:**
- Flexbox layout with gap
- Equal flex distribution
- Min-width for mobile breakpoint
- Border radius: 8px

---

### 6. Call-to-Action (CTA) Section
**Pattern:**
- Horizontal section with icon on left
- Text: "Are You Ready For The Perfect Summer?"
- Dark blue bar below with three buttons:
  - REQUEST INFO (envelope icon)
  - ENROLL NOW (checkbox icon)
  - DATES & TUITION (calendar icon)
- Buttons: White text on dark blue background

**Implementation:**
```html
<div class="cta-section" style="background: #f8f9fa; padding: 3rem 2rem; margin: 3rem 0; text-align: center;">
  <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1.5rem;">
    <span style="font-size: 2rem;">☀️</span>
    <h3 style="margin: 0; font-size: 1.75rem; font-weight: bold;">Are You Ready For The Perfect Summer?</h3>
  </div>
  <div style="background: #1a3a5c; padding: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
    <a href="#" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      📧 REQUEST INFO
    </a>
    <a href="#" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      ✓ ENROLL NOW
    </a>
    <a href="#" style="color: white; padding: 0.75rem 1.5rem; text-decoration: none; font-weight: bold; border-radius: 4px;">
      📅 DATES & TUITION
    </a>
  </div>
</div>
```

**Key Cues:**
- Light background (#f8f9fa) for section
- Icon + text centered
- Dark blue bar (#1a3a5c) for buttons
- White text on buttons
- Generous padding (3rem vertical, 2rem horizontal)
- Flexbox for responsive button layout

---

## 📐 Spacing Standards

### Vertical Spacing
- **Between major sections:** 3rem (48px)
- **Between paragraphs:** 1.5rem (24px)
- **Around images:** 2rem (32px)
- **Around content boxes:** 2.5rem (40px)
- **CTA section margins:** 3rem top/bottom

### Horizontal Spacing
- **Content padding:** 2rem (32px) on sides
- **Button gaps:** 1rem (16px)
- **Image gaps:** 1rem (16px)

---

## 🖼️ Image Standards

### Sizing
- **Hero images:** Full width, auto height (maintain aspect ratio)
- **Large images:** Max height 500px, full width
- **Side-by-side:** 50% width each (with gap)
- **Thumbnails:** Max width 300px

### Styling
- **Border radius:** 8px (rounded corners)
- **Object-fit:** cover (for fixed-height containers)
- **Display:** block (removes inline spacing)
- **Box shadow:** Optional subtle shadow for depth

---

## 🔗 Link & Button Standards

### Internal Links
- **Color:** Match site theme (blue: #0066cc or #1a3a5c)
- **Hover:** Slightly darker or underline
- **Text:** Descriptive anchor text (not "click here")

### CTA Buttons
- **Background:** Dark blue (#1a3a5c)
- **Text:** White, bold
- **Padding:** 0.75rem vertical, 1.5rem horizontal
- **Border radius:** 4px
- **Spacing:** 1rem gap between buttons

---

## 📝 Typography Standards

### Headings
- **H1/H2 (Main):** 2.5rem (40px), bold, line-height 1.3
- **H3 (Subsection):** 1.75rem (28px), bold, line-height 1.4
- **H4 (Minor):** 1.5rem (24px), semi-bold

### Body Text
- **Font size:** 1.05rem (16.8px base)
- **Line height:** 1.7-1.8
- **Color:** Dark gray (#333 or #444)

---

## 🎯 Layout Structure Template

```
[HERO IMAGE WITH OVERLAY BANNER]
  ↓ (3rem spacing)
[MAIN HEADING - H2]
  ↓ (1.5rem spacing)
[PARAGRAPH 1]
  ↓ (1.5rem spacing)
[PARAGRAPH 2]
  ↓ (2rem spacing)
[LARGE IMAGE - Full Width]
  ↓ (2rem spacing)
[PARAGRAPH 3]
  ↓ (1.5rem spacing)
[PARAGRAPH 4]
  ↓ (2rem spacing)
[SIDE-BY-SIDE IMAGES]
  ↓ (3rem spacing)
[CTA SECTION]
  - Icon + Text
  - Button Bar (3 buttons)
```

---

## ✅ Checklist for New Landing Pages

### Content Structure
- [ ] Hero image with overlay banner (dark blue, white text)
- [ ] Large, bold main heading (h2.page-title)
- [ ] Well-spaced paragraphs (1.5rem bottom margin)
- [ ] Large images at natural break points (max-height 500px)
- [ ] Side-by-side images where appropriate
- [ ] CTA section with icon, text, and buttons

### Spacing
- [ ] 3rem spacing between major sections
- [ ] 1.5rem spacing between paragraphs
- [ ] 2rem spacing around images
- [ ] 2.5rem spacing around content boxes

### Images
- [ ] All images have border-radius: 8px
- [ ] Large images: max-height 500px
- [ ] Responsive sizing (width: 100%, height: auto)
- [ ] Proper alt text for accessibility

### Links & Buttons
- [ ] Internal links use descriptive anchor text
- [ ] CTA buttons: dark blue background, white text
- [ ] Button spacing: 1rem gap
- [ ] All links resolve correctly

### Typography
- [ ] Main heading: 2.5rem, bold
- [ ] Body text: 1.05rem, line-height 1.7
- [ ] Adequate contrast for readability

---

## 🔄 Applying to New Pages

When creating new landing pages:

1. **Start with hero image** - Full width with overlay banner
2. **Add main heading** - Large, bold, 3rem from hero
3. **Structure content** - Paragraphs with 1.5rem spacing
4. **Insert images** - At natural break points, max-height 500px
5. **Add CTA section** - Icon + text + button bar
6. **Verify spacing** - Use spacing standards above
7. **Test responsive** - Ensure mobile-friendly layout

---

## 📋 Quick Reference

| Element | Spacing | Size | Color |
|---------|---------|------|-------|
| Hero overlay | Bottom-right | 1rem padding | Dark blue (#1a3a5c) |
| Main heading | 3rem top, 1.5rem bottom | 2.5rem | Dark (#333) |
| Paragraphs | 1.5rem bottom | 1.05rem | Dark gray (#444) |
| Large images | 2rem top/bottom | Max 500px height | - |
| CTA section | 3rem top/bottom | - | Light gray bg (#f8f9fa) |
| CTA buttons | 1rem gap | - | Dark blue (#1a3a5c) |

---

*This template is based on the "Our Story" page (ID: 1292) and should be used as a reference for all new landing pages.*
