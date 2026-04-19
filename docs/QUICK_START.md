# Quick Start Guide

Get up and running with the WordPress Publisher in 5 minutes.

---

## 🚀 Prerequisites

- Python 3.8 or higher
- WordPress site with REST API enabled
- WordPress admin access

---

## 📋 Step-by-Step Setup

### 1. Create/clone your client repository

This repository is intended to be used as a **GitHub Template**. Create a new repo per client, then clone it locally.

```bash
git clone YOUR_CLIENT_REPO_GIT_URL
cd YOUR_CLIENT_REPO_FOLDER
```

### 2. Install Dependencies

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Copy the template
cp env.example .env

# Edit .env with your details
nano .env  # or use your preferred editor
```

### 3b. Create client safety config (recommended)

This repo is intended to be used as a template for multiple clients. To prevent wrong-site publishing, create:

```bash
cp client.config.example.json client.config.json
```

Fill in `client.config.json` to match the site you expect to publish to.

**Required settings in `.env`:**
```bash
WP_SITE_URL=https://your-site.com
WP_USERNAME=your_admin_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**How to get Application Password:**
1. Log into WordPress Admin
2. Go to Users → Your Profile
3. Scroll to "Application Passwords"
4. Name it: "SEO Content Publisher"
5. Click "Add New Application Password"
6. Copy the generated password

### 4. Prepare Your Content

Add your content files to the appropriate directories:

```bash
content/
├── pages/          # Your 4 landing pages (JSON)
├── posts/          # Your 6 blog posts (JSON)
└── images/         # All images
```

**Content format:** See [CONTENT_REQUIREMENTS.md](CONTENT_REQUIREMENTS.md) for details.

### 5. Test Connection

```bash
./.venv/bin/python scripts/publisher/test_connection.py
```

This will validate:
- ✅ WordPress connection
- ✅ Authentication
- ✅ Permissions (publish posts/pages, upload, etc.)

### 6. Publish Content

```bash
# Publish ONE item (recommended)
./.venv/bin/python scripts/publisher/publish_content_item.py /absolute/path/to/content/posts/my-post.json --type posts

# Or publish a batch directory
./.venv/bin/python scripts/publisher/publish_batch.py /absolute/path/to/content/posts --type posts
```

---

## 📈 SEO planning (Sheets/Semrush/DataForSEO)

If you’re running the SEO planning pipeline, the scripts live under `scripts/seo/`.
If you have a paid DataForSEO plan (Keywords/SERP + Backlinks; AI Optimization optional), put credentials in `.env` (`DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD`).

Typical workflow:

1. Generate/update CSVs in `work/seo/…`
2. Push them into the planning Google Sheet:

```bash
./.venv/bin/python scripts/seo/push_seo_csvs_to_sheet.py --spreadsheet-id YOUR_SHEET_ID --project-root "$(pwd)"
```

---

## 🆘 Common Issues

### "401 Unauthorized"
**Fix:** Check your username and application password in `.env`

### "404 Not Found"
**Fix:** Verify `WP_SITE_URL` is correct (no trailing slash)

### "Application Passwords option missing"
**Fix:** 
- Ensure WordPress 5.6+
- Check with hosting provider (some disable it)
- Try JWT authentication (advanced)

### "Module not found"
**Fix:** Reinstall dependencies
```bash
./.venv/bin/python -m pip install -r requirements.txt
```

---

## 📚 Next Steps

- Read [SECURITY.md](SECURITY.md) for security best practices
- Check [ROADMAP.md](ROADMAP.md) for development phases
- Review [BACKUP_RESTORE.md](BACKUP_RESTORE.md) for backup strategies
- See [GITHUB_SETUP.md](GITHUB_SETUP.md) for repository management

---

## 🎯 Project Structure Overview

```
repo-root/
├── scripts/publisher/      # Canonical WordPress CLIs + legacy modules/ package
│   ├── publish_content_item.py
│   ├── publish_batch.py
│   ├── test_connection.py
│   └── modules/            # Legacy wrappers (prefer agt_publisher_core)
├── requirements.txt
├── .env                    # Your credentials (git-ignored)
├── content/                # JSON posts/pages + images
│   ├── pages/
│   ├── posts/
│   └── images/
├── packages/core_py/       # agt_publisher_core library
└── scripts/                # seo/, content-system/, images/, legacy/, …
```

---

## ✅ Quick Checklist

Before running:
- [ ] Cloned repository
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Created `.env` from `env.example`
- [ ] Generated WordPress Application Password
- [ ] Added credentials to `.env`
- [ ] Prepared content files
- [ ] Tested with `DRY_RUN=true`
- [ ] Ready to publish!

---

## 📞 Need Help?

- **Security questions:** See [SECURITY.md](SECURITY.md)
- **Content format:** See [CONTENT_REQUIREMENTS.md](CONTENT_REQUIREMENTS.md)
- **Technical specs:** See [TECH_SPEC.md](TECH_SPEC.md)
- **Backup issues:** See [BACKUP_RESTORE.md](BACKUP_RESTORE.md)
- **GitHub issues:** [Report a bug](https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/issues)

---

**Time to complete:** ~5-10 minutes  
**Difficulty:** Easy  
**Result:** All Camp Lakota content published to WordPress! 🎉
