# Git Workflow & Branching Strategy

## 🌳 Branch Structure

### Main Branches

#### `main` (Production-Ready)
**Purpose:** Stable, tested, production-ready code
**Contains:**
- ✅ All documentation (README, ROADMAP, TECH_SPEC, SECURITY)
- ✅ Finalized Python modules
- ✅ Configuration templates (env.example, .gitignore)
- ✅ requirements.txt
- ✅ Tested and working scripts

**Protected Rules:**
- All code must be tested before merging
- Must pass validation checks
- Documentation must be up-to-date

#### `develop` (Active Development)
**Purpose:** Integration branch for features
**Contains:**
- 🚧 Work-in-progress features
- 🚧 Integrated modules being tested together
- 🚧 Latest development code

**Merges from:** Feature branches
**Merges to:** `main` (when stable)

---

### Feature Branches

#### `feature/authentication` 
Authentication module development
- WordPress REST API connection
- Application password handling
- Connection testing

#### `feature/content-processor`
Content parsing and validation
- JSON/Markdown parsing
- Content validation
- HTML conversion

#### `feature/image-uploader`
Media management
- Image upload to WordPress
- Metadata handling
- Media library integration

#### `feature/pages-publisher`
Landing page publishing
- Page creation via API
- Page-specific metadata
- Schema injection for pages

#### `feature/posts-publisher`
Blog post publishing
- Post creation via API
- Categories and tags
- Post-specific metadata

#### `feature/internal-linking`
Internal link management
- Link mapping
- URL replacement
- Link verification

#### `feature/schema-seo`
Schema and SEO optimization
- JSON-LD schema generation
- OpenGraph metadata
- SEO plugin integration

---

## 📋 What Goes Where

### Always Commit to `main`:
```
✅ Documentation files (*.md)
✅ Configuration templates (env.example)
✅ .gitignore
✅ requirements.txt
✅ Project structure (folders)
✅ Tested, working code
✅ README updates
```

### NEVER Commit to Any Branch:
```
❌ .env (actual credentials)
❌ logs/ directory
❌ __pycache__/
❌ *.pyc files
❌ Personal API keys
❌ Test output files
❌ Temporary files
```

### Commit to Feature Branches:
```
🚧 Work-in-progress modules
🚧 Experimental code
🚧 Draft documentation
🚧 Test scripts
```

---

## 🔄 Git Workflow Process

### Phase 1: Initial Setup (Now)
```bash
# Initialize and push documentation
git init
git add README.md ROADMAP.md TECH_SPEC.md SECURITY.md GIT_WORKFLOW.md
git add CONTENT_REQUIREMENTS.md .gitignore env.example
git commit -m "docs: initial project documentation and structure"
git branch -M main
git remote add origin https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher.git
git push -u origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

### Phase 2: Feature Development
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/authentication

# Work on feature
git add modules/auth.py
git commit -m "feat(auth): implement WordPress REST API authentication"

# Push feature branch
git push -u origin feature/authentication
```

### Phase 3: Merge Feature to Develop
```bash
# After testing feature
git checkout develop
git merge feature/authentication
git push origin develop

# Optional: Delete feature branch after merge
git branch -d feature/authentication
git push origin --delete feature/authentication
```

### Phase 4: Release to Main
```bash
# When develop is stable and tested
git checkout main
git merge develop
git tag -a v1.0.0 -m "Release v1.0.0: Initial working version"
git push origin main --tags
```

---

## 📝 Commit Message Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation only
- **style:** Code formatting (no logic change)
- **refactor:** Code restructuring
- **test:** Adding tests
- **chore:** Build process, dependencies

### Examples
```bash
# Good commit messages
git commit -m "feat(auth): add WordPress application password authentication"
git commit -m "docs: update SECURITY.md with application password setup"
git commit -m "fix(images): handle missing alt text gracefully"
git commit -m "feat(posts): implement category and tag creation"

# Bad commit messages
git commit -m "update"
git commit -m "fix stuff"
git commit -m "wip"
```

---

## 🏷️ Version Tagging

### Semantic Versioning: MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes (2.0.0)
- **MINOR:** New features, backwards-compatible (1.1.0)
- **PATCH:** Bug fixes (1.0.1)

### Project Milestones
```
v0.1.0 - Initial documentation and structure
v0.2.0 - Authentication module complete
v0.3.0 - Content processor complete
v0.4.0 - Image uploader complete
v0.5.0 - Pages publisher complete
v0.6.0 - Posts publisher complete
v0.7.0 - Internal linking complete
v0.8.0 - Schema & SEO complete
v0.9.0 - Testing and validation complete
v1.0.0 - First production release
```

---

## 🚀 Development Timeline with Git

### Week 1: Foundation
```
main ← docs: initial setup (v0.1.0)
  ↓
develop ← structure: create project folders
  ↓
feature/authentication ← feat: WordPress auth
  ↓ (tested & merged)
develop ← merge: authentication complete (v0.2.0)
```

### Week 2: Core Modules
```
develop
  ↓
feature/content-processor ← feat: content parsing
  ↓ (merged)
feature/image-uploader ← feat: media upload
  ↓ (merged)
develop ← all core modules (v0.4.0)
```

### Week 3: Publishing
```
develop
  ↓
feature/pages-publisher ← feat: landing pages
  ↓ (merged)
feature/posts-publisher ← feat: blog posts
  ↓ (merged)
develop ← publishing complete (v0.6.0)
```

### Week 4: Polish & Release
```
develop
  ↓
feature/internal-linking ← feat: link management
  ↓ (merged)
feature/schema-seo ← feat: schema & SEO
  ↓ (merged)
develop ← all features (v0.8.0)
  ↓ (full testing)
main ← release v1.0.0 🎉
```

---

## 🔒 Protected Files Checklist

Before any commit, verify:
- [ ] `.env` is in `.gitignore`
- [ ] No hardcoded credentials in code
- [ ] No personal information in comments
- [ ] No API keys in any file
- [ ] Test data is sanitized
- [ ] Logs directory is git-ignored

---

## 🤝 Collaboration Guidelines

### For Solo Development (You + AI Assistant)
1. Work primarily on `develop` branch
2. Create feature branches for major modules
3. Merge to `main` when stable
4. Tag releases for milestones

### If Adding Team Members Later
1. Require pull requests for `main` and `develop`
2. Code review before merging
3. Automated testing on pull requests
4. Branch protection rules on `main`

---

## 📊 Repository Structure on GitHub

```
AGT_Camp_Lakota_Content_publisher/
├── .github/
│   └── workflows/          # Future: GitHub Actions (optional)
├── modules/
│   ├── __init__.py
│   ├── auth.py
│   ├── content.py
│   ├── images.py
│   ├── metadata.py
│   └── links.py
├── content/
│   ├── pages/
│   ├── posts/
│   └── images/
├── logs/                   # git-ignored
├── .gitignore
├── .env                    # git-ignored
├── env.example
├── requirements.txt
├── config.py
├── publish.py
├── README.md
├── ROADMAP.md
├── TECH_SPEC.md
├── SECURITY.md
├── GIT_WORKFLOW.md
└── CONTENT_REQUIREMENTS.md
```

---

## 🎯 Current Status

**Current Branch:** `main`
**Next Step:** Initial commit and push
**Next Branch:** `develop` for active development

---

## Quick Reference Commands

```bash
# Check current branch
git branch

# Check status
git status

# Create and switch to new branch
git checkout -b feature/feature-name

# Switch branches
git checkout branch-name

# Pull latest changes
git pull origin branch-name

# Push changes
git push origin branch-name

# View commit history
git log --oneline

# View all branches
git branch -a

# Delete local branch
git branch -d feature-name

# Delete remote branch
git push origin --delete feature-name
```

---

## 🎉 Benefits of This Strategy

1. **Backup:** All work saved on GitHub
2. **History:** Track every change and decision
3. **Rollback:** Revert to any previous version
4. **Collaboration:** Easy to add team members
5. **Organization:** Clear separation of features
6. **Testing:** Safe space to experiment (feature branches)
7. **Milestones:** Tagged versions for reference
