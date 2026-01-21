# Backup & Restore Guide

Complete guide for backing up and restoring your Camp Lakota WordPress Publisher project.

---

## 🔄 Automatic Backups (via Git/GitHub)

### What's Automatically Backed Up

Every time you commit and push to GitHub:
- ✅ All code files
- ✅ All documentation
- ✅ Project structure
- ✅ Configuration templates
- ✅ Full commit history

### What's NOT Backed Up (By Design)
- ❌ `.env` file (contains credentials - intentionally excluded)
- ❌ `logs/` directory (regenerated on each run)
- ❌ `__pycache__/` (Python cache - regenerated)
- ❌ Test output files

---

## 📦 Creating Manual Backups

### 1. Full Project Backup (Recommended Before Major Changes)

```bash
# Create a timestamped backup
cd /Users/jasonmellet/Desktop
tar -czf AGT_Camp_Lakota_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  AGT_Camp_Lakota/ \
  --exclude='AGT_Camp_Lakota/.git' \
  --exclude='AGT_Camp_Lakota/__pycache__' \
  --exclude='AGT_Camp_Lakota/logs'

# This creates: AGT_Camp_Lakota_backup_20260112_143022.tar.gz
```

### 2. Backup Your .env File Separately (SECURE LOCATION!)

```bash
# Copy .env to a secure location (NOT in git repo!)
cp /Users/jasonmellet/Desktop/AGT_Camp_Lakota/.env \
   ~/Documents/secure_backups/camp_lakota_env_$(date +%Y%m%d).txt

# Or use encrypted backup
openssl enc -aes-256-cbc -salt \
  -in /Users/jasonmellet/Desktop/AGT_Camp_Lakota/.env \
  -out ~/Documents/secure_backups/camp_lakota_env_$(date +%Y%m%d).enc
```

### 3. Backup Content Files Before Publishing

```bash
# Before running the publisher, backup your content
cd /Users/jasonmellet/Desktop/AGT_Camp_Lakota
tar -czf content_backup_$(date +%Y%m%d).tar.gz content/

# Store in safe location
mv content_backup_*.tar.gz ~/Documents/camp_lakota_backups/
```

---

## 🔙 Restoring from Backups

### Scenario 1: Restore Entire Project from GitHub

```bash
# If you lost everything, clone from GitHub
cd /Users/jasonmellet/Desktop
git clone https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher.git AGT_Camp_Lakota
cd AGT_Camp_Lakota

# Restore your .env file from secure backup
cp ~/Documents/secure_backups/camp_lakota_env_YYYYMMDD.txt .env

# Or decrypt if encrypted
openssl enc -aes-256-cbc -d \
  -in ~/Documents/secure_backups/camp_lakota_env_YYYYMMDD.enc \
  -out .env

# Install dependencies
pip install -r requirements.txt

# You're ready to go!
```

### Scenario 2: Restore Specific Version

```bash
# List all available versions
git tag

# Checkout specific version
git checkout v0.5.0

# Or create new branch from that version
git checkout -b restore-v0.5.0 v0.5.0
```

### Scenario 3: Restore Single File

```bash
# Restore a file to its last committed state
git checkout HEAD -- publish.py

# Restore a file from specific commit
git checkout abc123 -- modules/auth.py

# Restore from specific version tag
git checkout v0.4.0 -- modules/content.py
```

### Scenario 4: Undo Last Commit (Local Only)

```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and discard changes (CAREFUL!)
git reset --hard HEAD~1
```

### Scenario 5: Restore from Manual Backup

```bash
# Extract manual backup
cd /Users/jasonmellet/Desktop
tar -xzf AGT_Camp_Lakota_backup_20260112_143022.tar.gz

# Restore .env
cp ~/Documents/secure_backups/camp_lakota_env_20260112.txt \
   AGT_Camp_Lakota/.env
```

---

## 🚨 Emergency Recovery Procedures

### Problem: Accidentally Deleted Project

**Solution:**
1. Clone from GitHub (see Scenario 1 above)
2. Restore `.env` from secure backup
3. Reinstall dependencies

**Time to Recover:** 5 minutes

### Problem: Broke the Code, Need to Go Back

**Solution:**
```bash
# See what changed
git log --oneline

# Go back to working version
git reset --hard abc123  # Replace with working commit hash

# Or create safety branch first
git branch broken-code
git reset --hard abc123
```

**Time to Recover:** 2 minutes

### Problem: Accidentally Committed .env File

**Solution:**
```bash
# Remove from git history (if not pushed yet)
git rm --cached .env
git commit -m "security: remove .env from tracking"

# If already pushed, need to:
# 1. Revoke the Application Password in WordPress
# 2. Generate new Application Password
# 3. Update .env with new password
# 4. Consider git history cleanup (advanced)
```

### Problem: Lost .env File

**Solution:**
1. Restore from secure backup (see above)
2. OR regenerate:
   - Log into WordPress admin
   - Go to Users → Profile → Application Passwords
   - Revoke old password
   - Generate new one
   - Update `.env` file

---

## 📋 Pre-Publishing Backup Checklist

Before publishing content to WordPress:

```bash
# 1. Commit all code changes
git add .
git commit -m "feat: ready to publish Camp Lakota content"
git push origin develop

# 2. Backup content files
tar -czf content_backup_$(date +%Y%m%d).tar.gz content/

# 3. Create full project backup
cd ..
tar -czf AGT_Camp_Lakota_backup_pre_publish_$(date +%Y%m%d).tar.gz \
  AGT_Camp_Lakota/ --exclude='.git'

# 4. Test with DRY_RUN first
cd AGT_Camp_Lakota
# Set DRY_RUN=true in .env
python publish.py

# 5. If test successful, run for real
# Set DRY_RUN=false in .env
python publish.py

# 6. Commit completion status
git add logs/
git commit -m "docs: content published successfully on $(date +%Y-%m-%d)"
git push origin develop
```

---

## 🏷️ Version Tagging Strategy

### When to Create Tags

Create a new version tag when:
- ✅ Completing a major milestone
- ✅ After successful publishing run
- ✅ Before making breaking changes
- ✅ When code is stable and tested

### How to Create Tags

```bash
# After major milestone
git tag -a v0.5.0 -m "v0.5.0: Landing pages publisher complete"
git push origin v0.5.0

# After successful content publish
git tag -a v1.0.0 -m "v1.0.0: All Camp Lakota content published"
git push origin v1.0.0

# List all tags
git tag

# View tag details
git show v1.0.0
```

### Rollback to Tagged Version

```bash
# Create branch from tag for testing
git checkout -b test-v0.4.0 v0.4.0

# Or reset current branch to tag (CAREFUL!)
git reset --hard v0.4.0
```

---

## 💾 Recommended Backup Schedule

### Daily (While Actively Developing)
- ✅ Commit to git after each feature/fix
- ✅ Push to GitHub at end of day

### Before Major Operations
- ✅ Create full manual backup
- ✅ Backup `.env` file separately
- ✅ Backup content files
- ✅ Create version tag

### Weekly (During Development)
- ✅ Create manual backup archive
- ✅ Verify GitHub backups are up to date
- ✅ Test restore procedure

### After Publishing to WordPress
- ✅ Commit logs to git
- ✅ Create version tag
- ✅ Create manual backup
- ✅ Store published content IDs

---

## 🔐 Secure Storage Locations

### Recommended Backup Locations

**Local (Encrypted):**
```
~/Documents/camp_lakota_backups/
  ├── env_backups/           # Encrypted .env files
  ├── project_backups/       # Full project archives
  └── content_backups/       # Content snapshots
```

**Cloud (Optional):**
- iCloud Drive (encrypted folder)
- Dropbox (encrypted)
- External hard drive
- Time Machine (macOS automatic)

**Never Store:**
- ❌ Unencrypted `.env` in cloud storage
- ❌ Credentials in git repositories
- ❌ API keys in public locations

---

## 📊 Recovery Time Objectives (RTO)

| Scenario | Recovery Time | Data Loss |
|----------|---------------|-----------|
| Single file corruption | 1 minute | None (git restore) |
| Entire project deleted | 5 minutes | None (git clone) |
| Lost .env file | 2 minutes | None (secure backup) |
| Need previous version | 2 minutes | None (git checkout) |
| Corrupt git repository | 10 minutes | None (clone from GitHub) |
| GitHub unavailable | 15 minutes | None (manual backup) |

---

## ✅ Backup Verification

### Monthly Verification Checklist

- [ ] Verify GitHub repository is accessible
- [ ] Test git clone from GitHub
- [ ] Verify all tags are present
- [ ] Check manual backups are readable
- [ ] Test decrypting .env backup
- [ ] Verify content backups extract properly
- [ ] Check backup file sizes are reasonable
- [ ] Ensure backup locations have space
- [ ] Update this documentation if needed

---

## 🛡️ Disaster Recovery Plan

### Level 1: Minor Issue (Single file problem)
1. Use `git checkout` to restore file
2. Time: 1 minute
3. No data loss

### Level 2: Major Issue (Project corrupted)
1. Clone from GitHub
2. Restore `.env` from secure backup
3. Reinstall dependencies
4. Time: 5 minutes
5. No data loss

### Level 3: Complete Disaster (GitHub + local both gone)
1. Restore from manual backup archive
2. Restore `.env` from encrypted backup
3. Re-initialize git if needed
4. Time: 15 minutes
5. Potential data loss: Only changes since last manual backup

---

## 📞 Quick Reference Commands

```bash
# Create quick backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz AGT_Camp_Lakota/

# Restore from GitHub
git clone https://github.com/Jasonmellet/AGT_Camp_Lakota_Content_publisher.git

# Restore single file
git checkout HEAD -- filename.py

# Go back one commit
git reset --hard HEAD~1

# List all versions
git tag

# Checkout specific version
git checkout v0.5.0

# See what changed
git log --oneline

# See differences
git diff

# Stash changes temporarily
git stash
git stash pop  # Restore stashed changes
```

---

## 🎯 Summary

Your project is protected by:
1. ✅ **GitHub** - Automatic versioned backups
2. ✅ **Git tags** - Named snapshots of milestones
3. ✅ **Manual archives** - Full project backups
4. ✅ **Encrypted .env** - Secure credential backups
5. ✅ **This guide** - Recovery procedures

**Recovery confidence: 99.9%** - You can always get back to any previous state! 🛡️
