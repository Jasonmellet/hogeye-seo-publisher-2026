# Next Steps - Quick Reference

**Last Session:** January 20, 2026  
**Current Status:** Dual engine ready ✅ — Feb SEO plan in Sheets + WP publishing pipeline validated

---

## 🎯 Where We Are Now

✅ **COMPLETED:**
- WordPress connection + permissions verified (`test_connection.py`)
- Homepage safety guardrails (protect countdown markers) + local backups (`work/wp_backups/`)
- Feb SEO plan built + pushed to Google Sheets (final 10 + briefs + execution checklists + measurement tabs)

⏸️ **PENDING:**
- Execute Feb Wave 1 + Wave 2 edits (draft → review → publish)
- Internal links for legacy Jan posts (if/when needed)
- Featured images for legacy Jan posts (if/when needed)

---

## 🚀 Quick Start for Next Session

### 1. Reconnect and Test (Always start here)
```bash
cd /Users/jasonmellet/Desktop/AGT_Camp_Lakota
./.venv/bin/python test_connection.py
```

### 2. Check Current Status
- Log into WordPress admin
- Go to Posts → All Posts
- Verify all 6 draft posts are there
- Check one post to see categories, tags, SEO metadata

---

## 🔄 Next priority tasks (Feb execution)

### Use the execution checklist tab
- Open the Google Sheet tab: `Feb_2026_execution_checklists`
- Work top-down by rank and phase (Preflight → Draft → Review → Publish → Measure)

### Run the publisher in draft-first mode
- Keep `DRY_RUN=true` for dry runs and rehearsal
- For actual draft updates, set `DRY_RUN=false` but keep `status=draft` for review

### Optional (later): Internal links
**Issue:** Posts contain `{{link:slug|text}}` placeholders instead of real links

**What to do:**
1. Create internal link resolution script
2. Query WordPress for all published posts/pages
3. Build slug → URL mapping
4. Replace all placeholders with actual `<a href="">` tags
5. Update all 6 posts

**Estimated time:** 1-2 hours to build and test

---

### Optional (later): Featured images

**Issue:** Posts have no featured images, causing CSS overlap

**What to do:**
1. Create or source images for each post (6 images needed)
2. Images should be:
   - 1200x630px (optimal for social sharing)
   - Relevant to post topic
   - Professional quality
3. Upload via WordPress Media Library or API
4. Assign to each post

**Options:**
- Use stock photos (Unsplash, Pexels)
- Have designer create custom graphics
- Use AI image generation (Midjourney, DALL-E)

---

### MEDIUM PRIORITY: Final Review

**Before publishing live:**
1. Read through each post in WordPress preview
2. Check formatting on mobile
3. Verify meta descriptions show correctly
4. Test that featured images display properly
5. Confirm internal links work (after resolution)
6. Check that header CSS doesn't overlap

---

### Optional (later): Landing pages

**What to do:**
1. Review `a-day-at-camp-update.json`
2. Review `water-sports-update.json`  
3. Test updating ONE page first
4. Verify it updates correctly (doesn't create duplicate)
5. Update remaining pages

**⚠️ WARNING:** These files have `_update_existing: true` which means they'll REPLACE existing page content!

---

## 📝 Scripts Available

### Testing & Connection
```bash
python test_connection.py              # Test WordPress API connection
```

### Publishing
```bash
python publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts
python publish_batch.py /absolute/path/to/content/posts --type posts
python resolve_internal_links.py --dry-run
python update_landing_page.py /absolute/path/to/content/pages/my-page.json
```

### What Each Script Does
| Script | Purpose | Safety Level |
|--------|---------|--------------|
| `test_connection.py` | Read-only connection test | ✅ 100% Safe |
| `publish_content_item.py` | Publish/update ONE item via canonical pipeline | ✅ Safe (defaults to draft) |
| `publish_batch.py` | Publish/update a batch via canonical pipeline | ⚠️ Batch operation (still draft-first) |
| `resolve_internal_links.py` | Replace `{{link:...}}` placeholders across site | ⚠️ Modifies existing content (use `--dry-run` first) |
| `update_landing_page.py` | Update an existing landing page via canonical pipeline | ⚠️ Modifies existing pages (kept as draft for review) |

**Note:** Older one-off “fix” scripts are now under `scripts/legacy/` and should not be used for monthly publishing.

---

## 🐛 Known Issues to Watch For

### 1. WordPress PHP Warnings
**Status:** Mitch (sysadmin) working on it  
**Impact:** API responses have warnings before JSON  
**Workaround:** Our scripts clean the response automatically  
**Check:** Ask Steph/Mitch if `WP_DEBUG_DISPLAY` has been fixed

### 2. Duplicate Posts
**Status:** Can happen during testing  
**Impact:** Same post appears twice in WordPress  
**Fix:** Manually delete duplicates from WordPress admin  
**Prevention:** Use `publish_all_blogs.py` which checks for existing posts

### 3. Internal Link Placeholders
**Status:** Expected, not a bug  
**Impact:** Links show as `{{link:...}}` text instead of clickable links  
**Fix:** Need to create link resolution script  
**Priority:** HIGH - should be done before publishing live

---

## 📋 Pre-Publishing Checklist

Before changing any posts from "draft" to "published":

- [ ] Internal links resolved and working
- [ ] Featured images added to all posts
- [ ] Meta titles and descriptions verified
- [ ] Categories and tags assigned
- [ ] Mobile formatting tested
- [ ] CSS header overlap fixed (or worked around)
- [ ] All placeholder text removed
- [ ] Spell check and grammar review
- [ ] WordPress PHP warnings fixed (optional but nice)

---

## 💾 Backup Reminder

**Before any major changes:**
1. Backup WordPress database
2. Backup WordPress files
3. Commit code changes to git

**Backup locations:**
- WordPress: Check with Mitch/Steph
- Code: Already in GitHub

---

## 🆘 If Something Goes Wrong

### Post Published with Errors
1. Don't panic - it's just a draft, not live
2. Edit the post in WordPress admin
3. Fix the issue manually
4. Or: update the JSON file and re-run the script

### Can't Connect to WordPress
1. Run `python test_connection.py`
2. Check `.env` file for correct credentials
3. Verify WordPress site is up
4. Contact Steph/Mitch if site issue

### Script Errors
1. Check error message carefully
2. Verify WordPress is accessible
3. Check if backup is in progress (might slow API)
4. Try again after waiting a minute

---

## 📞 Contacts

- **Content Owner:** Jason
- **WordPress Admin:** Steph → Mitch (technical)
- **Hosting/Server:** Check with Mitch

---

## 🎓 What You Learned This Session

1. **WordPress REST API** is powerful but requires careful handling
2. **Duplicate detection** is essential for re-running scripts
3. **Publishing as drafts first** is always the right move
4. **Metadata should be added in first pass**, not second (lesson learned!)
5. **PHP debug warnings** can break JSON parsing but don't stop functionality
6. **Rich console output** makes debugging much easier

---

## 📚 Useful Documentation

- **Project Status:** `PROJECT_STATUS.md` (comprehensive status report)
- **Changelog:** `CHANGELOG.md` (what changed when)
- **Git Workflow:** `GIT_WORKFLOW.md` (branching strategy)
- **Tech Spec:** `TECH_SPEC.md` (technical details)
- **Security:** `SECURITY.md` (authentication guide)

---

## ✅ Session Checklist for Next Time

**At Start:**
- [ ] Activate virtual environment
- [ ] Run connection test
- [ ] Check WordPress admin for current status
- [ ] Review this file for what to do next

**During Work:**
- [ ] Test with one item before bulk operations
- [ ] Save progress frequently
- [ ] Document what you're doing
- [ ] Watch for error messages

**At End:**
- [ ] Update `PROJECT_STATUS.md`
- [ ] Update `CHANGELOG.md`
- [ ] Commit code changes to git
- [ ] Note any issues for next session

---

**Remember:** We've made excellent progress! 6 blog posts with 20,000 words of content are now in WordPress. The hardest part is done. 🎉

*Updated: January 12, 2026*
