# URL Migration Plan - What to Expect Page

## Overview
Repositioning `/what-to-expect/` from staff-facing to parent-facing content.

---

## Current State

**URL:** https://www.camplakota.com/what-to-expect/  
**Content:** Staff employment information ("What to Expect" as a staff member)  
**Location in Menu:** Work at Lakota section  
**Status:** Live, indexed by Google

---

## Proposed New State

### Parent-Facing Page (Takes Over Prime URL)
**URL:** `/what-to-expect/` (KEEPS existing URL)  
**New Content:** First-timer's guide for parents  
**New Title:** "What to Expect at Sleep-Away Camp: A First-Timer's Guide to Camp Lakota"  
**Location in Menu:** Future Families section or standalone  
**Target Audience:** First-time sleepaway camp parents  
**SEO Priority:** High (enrollment driver)

### Staff-Facing Page (Moves to New URL)
**Old URL:** `/what-to-expect/`  
**New URL:** `/work-at-lakota/what-to-expect/`  
**Content:** Same staff employment information (relocated)  
**Location in Menu:** Work at Lakota → What to Expect  
**SEO Priority:** Lower (niche audience)

---

## Migration Steps

### Step 1: Prepare New Staff URL
1. Create new page at `/work-at-lakota/what-to-expect/`
2. Copy existing staff content from `/what-to-expect/`
3. Update any internal links pointing to staff page
4. Test new staff page is accessible

### Step 2: Set Up 301 Redirect
```
OLD: /what-to-expect/ (staff)
→ 301 Redirect to → /work-at-lakota/what-to-expect/
```

**Why 301?**
- Preserves any existing SEO value
- Tells Google the content permanently moved
- Ensures no broken links
- Maintains user experience for bookmarked URLs

### Step 3: Publish Parent Page
1. Publish new parent-facing content to `/what-to-expect/`
2. This will REPLACE the old staff content at that URL
3. Verify redirect is working
4. Check new page renders correctly

### Step 4: Update Navigation Menus
**Main Menu Changes:**
- Add "What to Expect" under "Future Families" section
- Update "Work at Lakota" → "What to Expect" to point to new staff URL

**Breadcrumbs:**
- Parent page: Home → Future Families → What to Expect
- Staff page: Home → Work at Lakota → What to Expect

### Step 5: Update Internal Links
Find and update any pages linking to `/what-to-expect/`:
- If link is staff-related → Update to `/work-at-lakota/what-to-expect/`
- If link is parent-related → Keep as `/what-to-expect/`

### Step 6: Update Sitemap
- Remove old `/what-to-expect/` (staff) from sitemap
- Add `/work-at-lakota/what-to-expect/` (staff new location)
- Add `/what-to-expect/` (parent content)
- Submit updated sitemap to Google Search Console

### Step 7: Google Search Console
1. Request removal of old URL from Google index
2. Submit new URLs for indexing
3. Monitor 404 errors for broken links
4. Check Core Web Vitals for new page

---

## SEO Considerations

### Parent Page SEO (Priority)
**Target Keywords:**
- "what to expect at sleepaway camp"
- "first time camp guide"
- "typical day at summer camp"
- "camp lakota daily schedule"
- "sleep away camp routine"

**Schema Markup:**
- Article Schema
- BreadcrumbList Schema
- Organization Schema

**Meta:**
- Title: "What to Expect at Sleep-Away Camp: A First-Timer's Guide to Camp Lakota"
- Description: "Discover what a typical day looks like at Camp Lakota. From morning lineup to evening activities, learn how we support first-time campers with structure, supervision, and care." (160 chars)

### Staff Page SEO (Lower Priority)
**Target Keywords:**
- "camp counselor what to expect"
- "working at summer camp"
- "camp staff expectations"

**No Schema needed** (simple informational page)

---

## Risk Assessment

### Low Risk:
- Parent page is more valuable SEO target
- Staff page has minimal search traffic
- 301 redirect preserves link equity
- Content improves user experience

### Mitigation:
- Monitor 404 errors for 30 days
- Check Google Analytics for traffic drops
- Update any missed internal links
- Resubmit sitemap after changes

---

## Timeline

**Day 1:**
- Create new staff page at `/work-at-lakota/what-to-expect/`
- Set up 301 redirect
- Update menus

**Day 2:**
- Publish parent page to `/what-to-expect/`
- Test all links
- Submit sitemap

**Week 1:**
- Monitor analytics
- Check for 404s
- Update any missed links

**Week 2-4:**
- Monitor Google Search Console
- Track keyword rankings
- Verify indexing

---

## WordPress Implementation

### Plugin Recommendations:
- **Redirection** (for 301 redirects)
- **Yoast SEO** or **Rank Math** (for meta/schema)
- **Broken Link Checker** (find internal link issues)

### Manual Steps:
1. Log into WordPress admin
2. Create new page: Work at Lakota → What to Expect
3. Copy existing content from /what-to-expect/
4. Install Redirection plugin
5. Add 301: `/what-to-expect/` → `/work-at-lakota/what-to-expect/`
6. Update `/what-to-expect/` with new parent content
7. Update menus via Appearance → Menus
8. Regenerate sitemap (Yoast/Rank Math)

---

## Success Metrics

### Measure After 30 Days:
- [ ] Zero 404 errors related to migration
- [ ] Parent page ranking for target keywords
- [ ] Increased time-on-page for `/what-to-expect/`
- [ ] Higher conversion rate (request info / enroll)
- [ ] Staff page accessible and functional

---

## Rollback Plan

If issues arise:
1. Remove 301 redirect
2. Restore original staff content to `/what-to-expect/`
3. Move parent content to temporary URL
4. Reassess strategy

**Rollback time:** <30 minutes

---

## Checklist

Before Migration:
- [ ] Backup entire WordPress site
- [ ] Export existing /what-to-expect/ content
- [ ] Document all pages linking to /what-to-expect/
- [ ] Test 301 redirect on staging site (if available)

During Migration:
- [ ] Create new staff page
- [ ] Set up 301 redirect
- [ ] Publish parent page
- [ ] Update navigation menus
- [ ] Update internal links
- [ ] Regenerate sitemap

After Migration:
- [ ] Test both URLs
- [ ] Verify redirect works
- [ ] Check mobile rendering
- [ ] Monitor Google Search Console
- [ ] Track analytics for 30 days
- [ ] Update this document with results

---

## Notes

- **Priority:** High (enrollment season content)
- **Complexity:** Medium (requires redirect + menu updates)
- **Risk:** Low (parent content more valuable)
- **Timeline:** 1-2 days implementation, 30 days monitoring

**Contact:** Jason for any migration questions or issues.
