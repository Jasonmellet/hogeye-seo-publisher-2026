# Technical Specification - Camp Lakota WordPress Publisher

## Technology Stack

### Core Technologies

- **Language:** Python 3.8+
- **API:** WordPress REST API v2
- **Authentication:** Application Passwords (HTTP Basic Auth)

### Dependencies

```
requests>=2.31.0          # HTTP requests to WordPress API
python-dotenv>=1.0.0      # Environment variable management
Pillow>=10.0.0           # Image processing (if needed)
jsonschema>=4.17.0       # Content validation
```

---

## System Architecture

### High-Level Flow

```
Content Files → Parser → Validator → API Client → WordPress
                                         ↓
                    Images → Uploader ──┘
```

### Module Breakdown

#### 1. **Authentication Module** (`modules/auth.py`)

- Handle WordPress authentication
- Store and validate credentials
- Generate authentication headers
- Test API connectivity

#### 2. **Content Processor** (`modules/content.py`)

- Parse content files (JSON/Markdown)
- Validate required fields
- Convert markdown to HTML
- Prepare content for API submission

#### 3. **Image Uploader** (`modules/images.py`)

- Upload images to WordPress media library
- Set alt text, titles, captions, descriptions
- Return media IDs for embedding
- Handle image optimization

#### 4. **Metadata Handler** (`modules/metadata.py`)

- Manage Yoast/RankMath SEO fields
- Set meta titles and descriptions
- Configure OpenGraph tags
- Generate schema JSON-LD markup

#### 5. **Internal Linking** (`modules/links.py`)

- Map content relationships
- Replace link placeholders with real URLs
- Update published content with links
- Verify link integrity

---

## WordPress REST API Endpoints

### Pages

```
POST   /wp-json/wp/v2/pages          # Create page
PUT    /wp-json/wp/v2/pages/{id}     # Update page
GET    /wp-json/wp/v2/pages          # List pages
```

### Posts

```
POST   /wp-json/wp/v2/posts          # Create post
PUT    /wp-json/wp/v2/posts/{id}     # Update post
GET    /wp-json/wp/v2/posts          # List posts
```

### Media

```
POST   /wp-json/wp/v2/media          # Upload image
PUT    /wp-json/wp/v2/media/{id}     # Update media metadata
```

### Categories/Tags

```
POST   /wp-json/wp/v2/categories     # Create category
POST   /wp-json/wp/v2/tags           # Create tag
```

---

## Data Structures

### Landing Page Schema

```json
{
  "title": "Page Title",
  "slug": "page-slug",
  "content": "<html>Page content</html>",
  "status": "publish",
  "meta": {
    "description": "Meta description",
    "keywords": "keyword1, keyword2"
  },
  "featured_image": "image-filename.jpg",
  "schema": {
    "type": "LocalBusiness",
    "data": {...}
  },
  "internal_links": [
    {"text": "Link Text", "target": "post-slug"}
  ]
}
```

### Blog Post Schema

```json
{
  "title": "Post Title",
  "slug": "post-slug",
  "content": "<html>Post content</html>",
  "excerpt": "Short excerpt",
  "status": "publish",
  "categories": ["Category Name"],
  "tags": ["tag1", "tag2"],
  "author": "Author Name",
  "date": "2026-01-12T10:00:00",
  "featured_image": "image-filename.jpg",
  "images": [
    {
      "filename": "image.jpg",
      "alt": "Alt text",
      "caption": "Caption text"
    }
  ],
  "schema": {
    "type": "Article",
    "data": {...}
  },
  "internal_links": [
    {"text": "Link Text", "target": "page-slug"}
  ]
}
```

### Image Metadata Schema

```json
{
  "filename": "camp-lakota-summer.jpg",
  "alt_text": "Children enjoying summer activities at Camp Lakota",
  "title": "Camp Lakota Summer Activities",
  "caption": "Summer camp activities",
  "description": "Full description for media library"
}
```

---

## Environment Configuration

### Required Environment Variables

```bash
# WordPress Site
WP_SITE_URL=https://example.com
WP_USERNAME=admin_user
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Optional Settings
DRY_RUN=false                # Test mode (don't publish)
LOG_LEVEL=INFO               # Logging verbosity
```

---

## Error Handling

### Strategy

1. **Validation First:** Validate all content before API calls
2. **Graceful Failures:** Log errors, continue with next item
3. **Rollback Capability:** Track published IDs for cleanup
4. **Detailed Logging:** Log all API interactions

### Error Types

- Authentication failures
- Content validation errors
- API rate limiting
- Image upload failures
- Missing required fields

---

## Security Considerations

1. **Credentials:** Store in `.env`, never commit
2. **API Access:** Use application passwords, not main password
3. **Input Validation:** Sanitize all content before upload
4. **HTTPS Only:** Enforce secure connections

---

## Performance Optimization

1. **Batch Operations:** Group similar API calls
2. **Caching:** Cache category/tag IDs
3. **Rate Limiting:** Respect WordPress API limits
4. **Parallel Uploads:** Upload images concurrently (if API supports)

---

## Testing Strategy

### Manual Testing

- Test with 1 page and 1 post first
- Verify on WordPress admin
- Check frontend display

### Validation Checks

- Schema validation with Google Rich Results Test
- Internal link checker
- Image metadata verification
- Mobile responsiveness

---

## Rollback Plan

1. Keep log of all published IDs
2. Create cleanup script to delete published content
3. Manual deletion via WordPress admin as fallback
