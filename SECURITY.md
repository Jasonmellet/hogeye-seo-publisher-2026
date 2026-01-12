# Security Guide - WordPress REST API Authentication

## 🔐 How WordPress REST API Authentication Works

### What is an Application Password?

WordPress uses **Application Passwords** (introduced in WordPress 5.6) - NOT your regular WordPress login password. This is much more secure because:

1. **Separate from login password** - If compromised, doesn't give access to your WordPress admin panel
2. **Revocable** - Can be deleted anytime without changing your main password
3. **Specific to application** - You can create multiple passwords for different apps
4. **Limited scope** - Only works with REST API, not the admin interface

### Authentication Method: HTTP Basic Auth

```
Authorization: Basic base64(username:application_password)
```

The script will:
1. Read credentials from `.env` file
2. Encode them with base64
3. Send in HTTP Authorization header
4. WordPress validates and grants API access

---

## 🛡️ Security Best Practices Implemented

### 1. Environment Variables (`.env` file)
**✅ SECURE**
```bash
# Stored in .env (git-ignored)
WP_SITE_URL=https://camplakota.com
WP_USERNAME=admin
WP_APP_PASSWORD=AbCd EfGh IjKl MnOp QrSt UvWx
```

**❌ NEVER DO THIS**
```python
# Hardcoded in script (visible in git!)
username = "admin"
password = "AbCd EfGh IjKl MnOp QrSt UvWx"
```

### 2. HTTPS Only
- All API calls enforce HTTPS
- Credentials encrypted in transit
- Certificate validation enabled

### 3. Git Protection
- `.env` is in `.gitignore`
- Only `.env.example` is committed (with placeholder values)
- Credentials never exposed in version control

### 4. Application Password Scope
- Read/write access to posts, pages, media
- NO access to:
  - User management
  - Plugin/theme installation
  - WordPress core settings
  - Database access

---

## 📋 How to Generate Application Password

### Step 1: Log into WordPress Admin
Navigate to: `https://your-site.com/wp-admin`

### Step 2: Go to Your User Profile
WordPress Admin → Users → Profile (or click your name in top right)

### Step 3: Scroll to "Application Passwords"
Near the bottom of the page, you'll see:

```
┌─────────────────────────────────────────┐
│ Application Passwords                    │
├─────────────────────────────────────────┤
│ New Application Password Name            │
│ ┌───────────────────────┐               │
│ │ Camp Lakota Publisher │ [Add New]     │
│ └───────────────────────────┘           │
└─────────────────────────────────────────┘
```

### Step 4: Create Password
1. Enter name: "Camp Lakota Publisher"
2. Click "Add New Application Password"
3. **Copy the generated password immediately** (shown only once!)

Example output:
```
AbCd EfGh IjKl MnOp QrSt UvWx
```

### Step 5: Add to `.env` File
```bash
WP_APP_PASSWORD=AbCd EfGh IjKl MnOp QrSt UvWx
```

**Important:** Keep the spaces in the password!

---

## 🔍 What Data Can We Access via REST API?

### ✅ What We CAN Read (GET requests)

#### Site Information
```
GET /wp-json/
- WordPress version
- Site name and description
- Available REST API routes
- Namespaces and endpoints
```

#### Posts & Pages
```
GET /wp-json/wp/v2/posts
GET /wp-json/wp/v2/pages
- All published posts/pages
- Titles, content, slugs
- Meta data (if exposed)
- Featured images
- Categories and tags
- Author information
- Publish dates
```

#### Categories & Tags
```
GET /wp-json/wp/v2/categories
GET /wp-json/wp/v2/tags
- All categories/tags
- IDs, names, slugs
- Post counts
```

#### Media Library
```
GET /wp-json/wp/v2/media
- All uploaded images
- URLs, dimensions
- Alt text, captions
- Upload dates
```

#### Users (Limited)
```
GET /wp-json/wp/v2/users
- Display names only (public info)
- Avatar URLs
- NOT: emails, roles (unless admin)
```

### ✅ What We CAN Write (POST/PUT requests)

```
POST /wp-json/wp/v2/posts        # Create posts
POST /wp-json/wp/v2/pages        # Create pages
POST /wp-json/wp/v2/media        # Upload images
POST /wp-json/wp/v2/categories   # Create categories
POST /wp-json/wp/v2/tags         # Create tags

PUT /wp-json/wp/v2/posts/{id}    # Update posts
PUT /wp-json/wp/v2/pages/{id}    # Update pages
```

### ❌ What We CANNOT Access

- WordPress core settings
- Plugin settings (unless plugin exposes REST endpoints)
- Theme files
- Database directly
- Other user passwords
- WordPress admin functions
- File system access
- Server configuration

---

## 🚨 Security Risks & Mitigations

### Risk 1: Credential Exposure
**Mitigation:**
- ✅ Use `.env` file (git-ignored)
- ✅ Never hardcode credentials
- ✅ Use `.env.example` for templates only

### Risk 2: Man-in-the-Middle Attacks
**Mitigation:**
- ✅ Enforce HTTPS only
- ✅ Validate SSL certificates
- ✅ Reject insecure connections

### Risk 3: Accidental Data Deletion
**Mitigation:**
- ✅ DRY_RUN mode for testing
- ✅ Detailed logging of all operations
- ✅ Confirmation before bulk operations

### Risk 4: Compromised Application Password
**Mitigation:**
- ✅ Easy to revoke in WordPress admin
- ✅ Doesn't compromise main account
- ✅ Can generate new password anytime

### Risk 5: Accidental Git Commit
**Mitigation:**
- ✅ `.env` in `.gitignore`
- ✅ Only `.env.example` committed
- ✅ Pre-commit hooks (optional)

---

## 🔄 Revoking Access

If credentials are compromised:

1. Log into WordPress Admin
2. Go to Users → Profile
3. Find "Application Passwords" section
4. Click "Revoke" next to "Camp Lakota Publisher"
5. Generate new password if needed

**The old password stops working immediately!**

---

## ✅ Security Checklist

Before running the script:
- [ ] WordPress 5.6+ is installed
- [ ] HTTPS is enabled on WordPress site
- [ ] `.env` file created from `.env.example`
- [ ] Application password generated
- [ ] `.env` is in `.gitignore`
- [ ] Never commit `.env` to git
- [ ] Test with DRY_RUN=true first

---

## 🧪 Testing Authentication

The script will test authentication before publishing:

```python
# Test connection
response = requests.get(
    f"{WP_SITE_URL}/wp-json/wp/v2/posts",
    auth=(username, app_password)
)

if response.status_code == 200:
    print("✅ Authentication successful!")
else:
    print("❌ Authentication failed!")
    print(f"Status: {response.status_code}")
    print(f"Error: {response.json()}")
```

---

## 📞 Troubleshooting

### "401 Unauthorized"
- Check username is correct
- Verify application password (with spaces)
- Ensure Application Passwords are enabled in WordPress

### "403 Forbidden"
- User doesn't have permission to create posts/pages
- Application Passwords might be disabled by host

### "404 Not Found"
- Check WP_SITE_URL is correct
- Verify REST API is enabled
- Check for security plugins blocking API

### Application Passwords Option Missing
Some hosts disable this. Solutions:
1. Contact hosting support to enable
2. Use JWT authentication (more complex)
3. Use OAuth (most complex)

---

## 🎯 Summary

**This approach is secure because:**
1. Separate authentication from main WordPress login
2. Credentials stored in git-ignored `.env` file
3. HTTPS encrypts all communication
4. Limited API scope (can't access admin panel)
5. Easy to revoke if compromised
6. No database or file system access

**You're safe to use this for your Camp Lakota content!** 🏕️
