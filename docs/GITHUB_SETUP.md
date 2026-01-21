# GitHub Repository Setup Guide

Complete guide for configuring your GitHub repository for optimal tracking, backup, and collaboration.

---

## 🔧 Repository Settings (Recommended)

### 1. General Settings

Navigate to: **Settings → General**

#### Default Branch
- ✅ Set default branch to `develop` (for active development)
- This ensures PRs and new work default to the development branch

```
Settings → General → Default branch
Change from: main
Change to: develop
```

#### Features to Enable
- ✅ Issues (for bug tracking and features)
- ✅ Projects (for kanban-style project management)
- ✅ Preserve this repository (archive for long-term storage)
- ❌ Wikis (not needed - we have markdown docs)
- ❌ Discussions (optional, for community)

---

### 2. Branch Protection Rules

Navigate to: **Settings → Branches → Add branch protection rule**

#### Protect `main` Branch

**Branch name pattern:** `main`

Enable these rules:
- ✅ **Require a pull request before merging**
  - Require approvals: 1 (if you add collaborators)
- ✅ **Require conversation resolution before merging**
- ✅ **Do not allow bypassing the above settings**
- ❌ **Allow force pushes** (keep disabled for safety)
- ❌ **Allow deletions** (keep disabled for safety)

#### Protect `develop` Branch (Optional)

**Branch name pattern:** `develop`

Less strict than main:
- ✅ **Require conversation resolution before merging**
- ✅ **Allow force pushes** (only by administrators)
- ❌ **Allow deletions**

---

### 3. Security Settings

Navigate to: **Settings → Code security and analysis**

#### Enable These Features:
- ✅ **Dependabot alerts** - Get notified of security vulnerabilities
- ✅ **Dependabot security updates** - Auto-update vulnerable dependencies
- ✅ **Secret scanning alerts** - Detect accidentally committed secrets
- ✅ **Push protection** - Block commits containing secrets

These will alert you if:
- Python packages have security vulnerabilities
- API keys or passwords are accidentally committed
- Dependencies are outdated

---

### 4. Notifications

Navigate to: **Settings → Notifications** (in your personal GitHub settings)

Recommended settings:
- ✅ Email notifications for: Participating, @mentions, and your activity
- ✅ GitHub Mobile app (for instant alerts)

---

## 🏷️ Labels for Issues & PRs

Navigate to: **Issues → Labels**

### Recommended Labels to Create:

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | 🔴 #d73a4a | Something isn't working |
| `enhancement` | 🟢 #a2eeef | New feature or request |
| `documentation` | 📘 #0075ca | Documentation improvements |
| `security` | 🔒 #ee0701 | Security-related issues |
| `urgent` | 🚨 #b60205 | Needs immediate attention |
| `wordpress-api` | 🔌 #0052cc | Related to WordPress REST API |
| `content` | 📝 #c5def5 | Content-related issues |
| `images` | 🖼️ #fbca04 | Image handling |
| `schema` | 🏗️ #d4c5f9 | Schema/SEO related |
| `good-first-issue` | 👋 #7057ff | Good for newcomers |
| `help-wanted` | 🆘 #008672 | Extra attention needed |
| `wontfix` | ⛔ #ffffff | Won't be fixed |
| `duplicate` | 🔄 #cfd3d7 | Already exists |

### Quick Import (Use GitHub's CLI)
```bash
# Install gh CLI first: brew install gh

gh label create "wordpress-api" --color "0052cc" --description "Related to WordPress REST API"
gh label create "content" --color "c5def5" --description "Content-related issues"
gh label create "images" --color "fbca04" --description "Image handling"
gh label create "schema" --color "d4c5f9" --description "Schema/SEO related"
gh label create "urgent" --color "b60205" --description "Needs immediate attention"
```

---

## 📊 Project Boards (Kanban)

Navigate to: **Projects → New project**

### Option 1: Simple Board

Create a board with columns:
1. **📋 Backlog** - Ideas and future tasks
2. **📝 To Do** - Planned for current phase
3. **🚧 In Progress** - Currently working on
4. **🧪 Testing** - Needs testing/review
5. **✅ Done** - Completed

### Option 2: Development Phases Board

Match your roadmap:
1. **Phase 1: Foundation** (auth, config)
2. **Phase 2: Content Processing**
3. **Phase 3: Images**
4. **Phase 4: Publishing**
5. **Phase 5: Polish** (linking, schema)
6. **✅ Completed**

### Auto-add Issues
Enable automation:
- ✅ New issues → Backlog
- ✅ Issues in progress → In Progress
- ✅ Closed issues → Done

---

## 🔔 GitHub Actions (Optional - Future)

Create `.github/workflows/` for automation:

### 1. Python Linting (Future)
```yaml
# .github/workflows/lint.yml
name: Lint Python

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install flake8
      - run: flake8 . --max-line-length=120
```

### 2. Security Scanning
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
```

**Note:** These are optional - implement when you want automated testing.

---

## 📦 Releases

Navigate to: **Releases → Create a new release**

### When to Create a Release

Create releases for:
- ✅ Major milestones (v0.5.0, v1.0.0)
- ✅ After successful content publishing
- ✅ When code is stable and tested

### Release Template
```markdown
## Camp Lakota Publisher v0.5.0

### 🎉 New Features
- Landing pages publisher module complete
- Support for custom meta fields
- Schema markup injection

### 🐛 Bug Fixes
- Fixed image upload timeout issue
- Improved error handling in auth module

### 📝 Documentation
- Updated TECH_SPEC.md with API examples
- Added troubleshooting guide

### ⬆️ Upgrade Notes
No breaking changes from v0.4.0

### 📦 Installation
\```bash
git clone https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher.git
cd AGT_Camp_Lakota_Content_publisher
git checkout v0.5.0
pip install -r requirements.txt
\```

### 🔗 Full Changelog
See [CHANGELOG.md](CHANGELOG.md) for detailed changes
```

---

## 🔍 GitHub Insights to Monitor

Navigate to: **Insights**

### Useful Graphs:
- **Pulse** - Recent activity summary
- **Contributors** - Who's contributing
- **Commits** - Commit frequency
- **Code frequency** - Lines added/removed
- **Network** - Branch visualization

---

## 🛡️ Security Best Practices

### 1. .env File Protection
Already configured in `.gitignore`:
```
.env
*.env
.env.*
!.env.example
```

### 2. Secret Scanning Alerts
If you accidentally commit secrets:
1. GitHub will alert you immediately
2. Revoke the WordPress Application Password
3. Generate new credentials
4. Update .env locally
5. Consider using `git filter-branch` to remove from history

### 3. Dependabot
Will create PRs to update vulnerable packages:
- Review the PR
- Test locally
- Merge when safe

---

## 📋 Repository Maintenance Checklist

### Weekly
- [ ] Check for open issues
- [ ] Review Dependabot alerts
- [ ] Verify backups are current
- [ ] Check branch status

### Monthly
- [ ] Review and update documentation
- [ ] Clean up merged branches
- [ ] Update dependencies
- [ ] Create release if milestone reached

### After Major Changes
- [ ] Tag new version
- [ ] Update CHANGELOG.md
- [ ] Create GitHub release
- [ ] Merge develop → main (if stable)

---

## 🤝 Collaborator Settings (If Adding Team)

Navigate to: **Settings → Collaborators and teams**

### Access Levels:
- **Admin** - Full access (you)
- **Write** - Can push to develop, create PRs
- **Read** - View only

### Recommended for Team:
1. Require PRs for all changes to `main`
2. Require 1 review before merging
3. Use feature branches for all work
4. Tag releases after testing

---

## 📱 GitHub Mobile App

### Download & Configure
1. Install GitHub Mobile (iOS/Android)
2. Enable push notifications
3. Get instant alerts for:
   - Issues assigned to you
   - PR reviews requested
   - Security alerts
   - Pipeline failures

---

## 🔗 Repository Links to Bookmark

- **Main Repo:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher
- **Issues:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/issues
- **PRs:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/pulls
- **Projects:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/projects
- **Releases:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/releases
- **Security:** https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher/security

---

## ✅ Setup Completion Checklist

- [ ] Repository created and pushed
- [ ] Default branch set to `develop`
- [ ] Branch protection rules configured
- [ ] Security features enabled (Dependabot, secret scanning)
- [ ] Issue templates added
- [ ] PR template added
- [ ] Labels created
- [ ] Project board created (optional)
- [ ] README badges added (optional)
- [ ] GitHub Mobile app installed
- [ ] Documentation reviewed
- [ ] CHANGELOG.md initialized
- [ ] First release created (v0.1.0)

---

## 🎯 Summary

Your GitHub repository now has:
1. ✅ **Automated backups** via git push
2. ✅ **Version tracking** via tags and releases
3. ✅ **Issue tracking** with templates
4. ✅ **Security scanning** for secrets and vulnerabilities
5. ✅ **Branch protection** to prevent accidents
6. ✅ **Professional structure** for future collaboration

**Ready for development!** 🚀
