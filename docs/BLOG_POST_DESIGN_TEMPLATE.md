# Blog Post Design Template
## Based on "Why Sleep-Away Summer Camp Near NYC Builds Confidence & Connection" Analysis

**Reference Post:** `/why-sleep-away-summer-camp-near-nyc-builds-confidence-connection/` (ID: 2641)  
**Last Updated:** January 2026

---

## 🎨 Visual Design Patterns

### 1. Hero Section (Theme-Controlled)
**Pattern:**
- Dark blue banner background (#1a3a5c or similar)
- White text, centered
- Large, bold title
- Subtle design elements (mountain silhouette at bottom)

**Note:** This is typically handled by the WordPress theme, not in post content.

**Key Cues:**
- Dark blue background for contrast
- White text for readability
- Large, prominent title
- Full-width banner

---

### 2. Featured Image
**Pattern:**
- Large, prominent image
- Positioned on **left side** of content area
- Width: Approximately 600-800px (or 40-50% of content width)
- High quality, relevant to post topic
- Text flows around or below image

**Implementation:**
```html
<!-- Featured image is set via WordPress featured image field -->
<!-- Theme displays it prominently at top of post -->
```

**Key Cues:**
- Large enough to be prominent (not thumbnail)
- Left-aligned or floated left
- Relevant to post content
- High quality, engaging image

---

### 3. Content Structure & Typography

#### Main Heading (H1/H2)
**Pattern:**
- Large, bold heading for main sections
- Clear visual hierarchy
- Adequate spacing above and below

**Implementation:**
```html
<h2 style="font-size: 2rem; font-weight: bold; margin-top: 2.5rem; margin-bottom: 1.5rem; line-height: 1.3;">
  Sleep-Away Summer Camp Near NYC with Time-Honoured Traditions
</h2>
```

**Key Cues:**
- Font size: 2rem (32px) for main headings
- Font weight: Bold
- Top margin: 2.5rem (spacing from previous section)
- Bottom margin: 1.5rem (spacing to content)

#### Subheadings (H3, H4)
**Pattern:**
- Smaller than main headings
- Still bold for emphasis
- Clear hierarchy

**Implementation:**
```html
<h3 style="font-size: 1.5rem; font-weight: bold; margin-top: 2rem; margin-bottom: 1rem;">
  Subsection Title
</h3>
```

**Key Cues:**
- H3: 1.5rem (24px)
- H4: 1.25rem (20px)
- Progressive sizing for hierarchy

#### Paragraphs
**Pattern:**
- Clean, readable text
- Adequate line spacing
- Consistent bottom margin

**Implementation:**
```html
<p style="margin-bottom: 1.5rem; line-height: 1.7; font-size: 1rem;">
  Paragraph content here...
</p>
```

**Key Cues:**
- Line height: 1.7 for readability
- Bottom margin: 1.5rem between paragraphs
- Font size: 1rem (16px) base

---

### 4. Internal Links
**Pattern:**
- Natural integration within content
- Descriptive anchor text (not "click here")
- Links to relevant pages/posts
- Styled as standard links (blue, underlined on hover)

**Examples from Reference:**
- "Visit the **Why Lakota** page..." → `{{link:why-lakota|Why Lakota}}`
- "Consider participating in **Rookie Day**..." → `{{link:rookie-day-experience|Rookie Day}}`
- "**Enroll Now** or **Request Info**..." → `{{link:enroll-now|Enroll Now}}` and `{{link:contact|Request Info}}`

**Implementation:**
```html
<p>Visit the <a href="https://www.camplakota.com/why-lakota/">Why Lakota</a> page to review our values...</p>
```

**Key Cues:**
- Anchor text is descriptive and natural
- Links are integrated into sentences
- Not overused (2-5 links per post section)
- Links to relevant, related content

---

### 5. Bullet Lists / CTA Section
**Pattern:**
- Clean bullet list at end of post
- Each item is an action item
- Links embedded naturally in list items
- Clear, actionable language

**Structure:**
```html
<ul style="margin: 2rem 0; padding-left: 2rem; line-height: 1.8;">
  <li style="margin-bottom: 1rem;">
    Visit the <a href="...">Why Lakota</a> page to review our values, mission and community commitment.
  </li>
  <li style="margin-bottom: 1rem;">
    Consider participating in <a href="...">Rookie Day</a>—our one-day experience where future campers sample life at camp...
  </li>
  <li style="margin-bottom: 1rem;">
    Review sessions, dates and tuition to align your summer planning and budget.
  </li>
  <li style="margin-bottom: 1rem;">
    If you're ready, <a href="...">Enroll Now</a> or <a href="...">Request Info</a> and come for a tour...
  </li>
</ul>
```

**Key Cues:**
- List items: 1rem bottom margin
- Line height: 1.8 for readability
- Padding-left: 2rem for bullet spacing
- Action-oriented language
- Links embedded naturally

---

### 6. Content Flow
**Pattern:**
- Introduction paragraph(s) at start
- Main sections with H2 headings
- Subsections with H3 headings
- Natural progression of information
- CTA section at end

**Structure:**
```
[Featured Image - Left Side]
  ↓
[Introduction Paragraphs]
  ↓
[H2: Main Section 1]
  [Paragraphs]
  [H3: Subsection]
    [Paragraphs]
  ↓
[H2: Main Section 2]
  [Paragraphs]
  ↓
[H2: Main Section 3]
  [Paragraphs]
  ↓
[CTA Section - Bullet List with Links]
```

---

## 📐 Spacing Standards

### Vertical Spacing
- **Between major sections (H2):** 2.5rem (40px) top margin
- **Between paragraphs:** 1.5rem (24px) bottom margin
- **Between subsections (H3):** 2rem (32px) top margin
- **Around lists:** 2rem (32px) top/bottom margin
- **After featured image:** 2rem (32px) before content starts

### Horizontal Spacing
- **Content padding:** 2rem (32px) on sides (theme-controlled)
- **List padding:** 2rem (32px) left for bullets

---

## 🔗 Link Standards

### Internal Links
- **Anchor text:** Descriptive and natural (e.g., "Why Lakota", "Rookie Day", "Enroll Now")
- **Integration:** Embedded naturally in sentences
- **Frequency:** 2-5 links per major section
- **Style:** Standard link styling (blue, underlined on hover)

### CTA Links
- **Location:** End of post in bullet list
- **Format:** Action-oriented language
- **Examples:**
  - "Visit the [Why Lakota] page..."
  - "Consider participating in [Rookie Day]..."
  - "[Enroll Now] or [Request Info]..."

---

## 📝 Typography Standards

### Headings
- **H1/H2 (Main):** 2rem (32px), bold, line-height 1.3
- **H3 (Subsection):** 1.5rem (24px), bold, line-height 1.4
- **H4 (Minor):** 1.25rem (20px), semi-bold

### Body Text
- **Font size:** 1rem (16px) base
- **Line height:** 1.7 for paragraphs, 1.8 for lists
- **Color:** Dark gray (#333 or #444)

---

## 🖼️ Featured Image Standards

### Sizing & Position
- **Width:** 600-800px (or 40-50% of content width)
- **Position:** Left side of content
- **Display:** Prominent, not thumbnail-sized
- **Responsive:** Scales down on mobile

### Content
- **Relevance:** Directly related to post topic
- **Quality:** High resolution, professional
- **Alt text:** Descriptive and SEO-friendly

---

## ✅ Checklist for New Blog Posts

### Content Structure
- [ ] Featured image set (large, relevant, left-aligned)
- [ ] Introduction paragraph(s) at start
- [ ] Clear heading hierarchy (H2 for main, H3 for subsections)
- [ ] Well-spaced paragraphs (1.5rem bottom margin)
- [ ] Internal links integrated naturally (2-5 per section)
- [ ] CTA section at end with bullet list

### Spacing
- [ ] 2.5rem spacing between major sections (H2)
- [ ] 1.5rem spacing between paragraphs
- [ ] 2rem spacing around lists
- [ ] 2rem spacing after featured image

### Links
- [ ] Descriptive anchor text (not "click here")
- [ ] Links integrated naturally in sentences
- [ ] CTA links at end in bullet format
- [ ] All links resolve correctly

### Typography
- [ ] Main headings: 2rem, bold
- [ ] Body text: 1rem, line-height 1.7
- [ ] List items: line-height 1.8
- [ ] Adequate contrast for readability

---

## 🎯 Blog Post Structure Template

```
[HERO BANNER - Theme Controlled]
  Dark blue background, white text title
  ↓
[FEATURED IMAGE - Left Side]
  Large, prominent image (600-800px width)
  ↓ (2rem spacing)
[INTRODUCTION PARAGRAPH(S)]
  Sets context, introduces topic
  ↓ (1.5rem spacing)
[H2: MAIN SECTION 1]
  [Paragraphs with 1.5rem spacing]
  [H3: Subsection]
    [Paragraphs]
  ↓ (2.5rem spacing)
[H2: MAIN SECTION 2]
  [Paragraphs with internal links]
  ↓ (2.5rem spacing)
[H2: MAIN SECTION 3]
  [Paragraphs]
  ↓ (2.5rem spacing)
[CTA SECTION]
  <ul>
    <li>Action item with link</li>
    <li>Action item with link</li>
    <li>Action item with link</li>
  </ul>
```

---

## 📋 Quick Reference

| Element | Spacing | Size | Style |
|---------|---------|------|-------|
| H2 (Main) | 2.5rem top, 1.5rem bottom | 2rem | Bold |
| H3 (Sub) | 2rem top, 1rem bottom | 1.5rem | Bold |
| Paragraphs | 1.5rem bottom | 1rem | Normal |
| Lists | 2rem top/bottom | - | 1.8 line-height |
| Featured Image | 2rem bottom | 600-800px | Left-aligned |
| Internal Links | Natural in text | - | Blue, underlined |

---

## 🔄 Key Differences from Landing Pages

### Blog Posts:
- ✅ **Featured image** is prominent and left-aligned (not hero banner)
- ✅ **No overlay banners** (theme handles hero)
- ✅ **More text-heavy** content
- ✅ **CTA at end** (not mid-page)
- ✅ **Internal links** more integrated in content
- ✅ **Bullet lists** for CTA actions

### Landing Pages:
- ✅ **Hero image** with overlay banner
- ✅ **More visual** (images throughout)
- ✅ **CTA section** with icon + button bar
- ✅ **Side-by-side images**
- ✅ **Content boxes** for emphasis

---

## 💡 Best Practices

### Content Flow
1. **Start strong:** Engaging introduction that hooks reader
2. **Clear structure:** Use headings to break up long content
3. **Natural links:** Integrate links where they add value
4. **End with action:** CTA section guides next steps

### Link Integration
- ✅ "Visit our [Why Lakota] page to learn more..."
- ✅ "Consider [Rookie Day] for first-time campers..."
- ❌ "Click here to learn more" (not descriptive)
- ❌ "For more info, visit this page" (unnatural)

### Readability
- Keep paragraphs to 3-5 sentences
- Use bullet lists for multiple points
- Break up long sections with subheadings
- Use bold text sparingly for emphasis

---

*This template is based on the "Why Sleep-Away Summer Camp Near NYC Builds Confidence & Connection" post (ID: 2641) and should be used as a reference for all new blog posts.*
