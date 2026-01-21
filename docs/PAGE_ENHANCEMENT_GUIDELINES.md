# Page Enhancement Guidelines

## 🚨 Critical Rules to Prevent Poor Editing

### 1. **Always Make Scripts Idempotent**
- ✅ **DO**: Check if elements already exist before inserting
- ❌ **DON'T**: Blindly insert elements every time script runs
- **Why**: Prevents duplicates when script runs multiple times

```python
# ✅ GOOD: Check first
if unique_class in content:
    return content  # Skip if exists

# ❌ BAD: Always insert
content = insert_element(content)  # Creates duplicates
```

### 2. **Avoid Redundant Information**
- ✅ **DO**: Place content boxes that ADD value, not repeat existing text
- ❌ **DON'T**: Create boxes that duplicate nearby paragraphs
- **Example**: Don't add "Daily Schedule" box right after "Daily Rhythm" section that already explains the schedule

### 3. **Proper Spacing**
- ✅ **DO**: Add adequate margins (2-2.5rem) between elements
- ❌ **DON'T**: Place elements back-to-back without spacing
- **Rule**: Content boxes and images should have `margin: 2.5rem 0;`

### 4. **Image Placement Strategy**
- ✅ **DO**: Place images AFTER relevant text sections
- ✅ **DO**: Use unique CSS classes for each image to prevent duplicates
- ❌ **DON'T**: Insert images in the middle of paragraphs
- ❌ **DON'T**: Place multiple images too close together

### 5. **Content Box Placement**
- ✅ **DO**: Place boxes at natural break points (after headings, before new sections)
- ✅ **DO**: Use boxes to highlight key information, not repeat it
- ❌ **DON'T**: Interrupt the flow of a narrative section

### 6. **Link Resolution Timing**
- ✅ **DO**: Resolve links AFTER all pages are published
- ❌ **DON'T**: Try to resolve links to pages that don't exist yet
- **Note**: Some placeholders may remain until target pages are created

### 7. **Testing Before Production**
- ✅ **DO**: Test scripts on draft pages first
- ✅ **DO**: Review preview before publishing
- ✅ **DO**: Check for duplicates after running scripts
- ❌ **DON'T**: Run enhancement scripts multiple times without checking

## 📋 Enhancement Checklist

Before running any enhancement script:

- [ ] Script is idempotent (safe to run multiple times)
- [ ] Checks for existing elements before inserting
- [ ] Removes duplicates if found
- [ ] Uses unique identifiers (CSS classes) for each element
- [ ] Adds proper spacing (2-2.5rem margins)
- [ ] Content boxes don't duplicate nearby text
- [ ] Images are placed at logical break points
- [ ] Script can be safely re-run without issues

## 🔧 Script Template

```python
def insert_element(content: str, unique_id: str) -> str:
    """Insert element only if not already present"""
    
    # Check if already exists
    if unique_id in content:
        console.print(f"[dim]Element {unique_id} already exists, skipping...[/dim]")
        return content
    
    # Insert logic here
    # ...
    
    return content
```

## 🎯 Content Box Best Practices

### When to Use Content Boxes:
- ✅ Highlighting key safety features
- ✅ Summarizing important information
- ✅ Creating visual breaks in long text
- ✅ Emphasizing call-to-action sections

### When NOT to Use:
- ❌ Repeating information already in nearby paragraphs
- ❌ Breaking up a narrative flow
- ❌ Adding boxes just for decoration

## 🖼️ Image Best Practices

### Placement:
- After section headings (not before)
- After relevant paragraphs (not in middle)
- With adequate spacing (2.5rem margin)
- With descriptive captions when helpful

### Styling:
- Use `border-radius: 8px` for modern look
- Add `box-shadow` for depth
- Center-align with `text-align: center`
- Responsive: `max-width: 100%; height: auto;`

## 📝 Current Script Status

**GOLD STANDARD**: `rebuild_page_properly.py`
- ✅ Starts from clean source (no duplicates possible)
- ✅ Adds proper padding to ALL paragraphs (1.5rem bottom)
- ✅ Adds proper spacing to ALL headings (2-3rem top)
- ✅ Images with consistent formatting (3rem margins, max-width 900px)
- ✅ Content boxes with proper spacing (3rem margins)
- ✅ No duplicate sections
- ✅ Professional, clean layout

**Workflow:**
1. Load clean source JSON
2. Add padding to all elements
3. Insert images with consistent formatting
4. Add content boxes where they add value
5. Update WordPress page

**Previous Script**: `fix_and_enhance_page.py` (deprecated - use rebuild approach instead)

## 🚀 Future Enhancements

When adding new enhancement features:
1. Follow idempotent pattern
2. Add unique identifiers
3. Test on draft page first
4. Review preview before publishing
5. Document in this file
