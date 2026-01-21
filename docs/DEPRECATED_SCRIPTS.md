# Deprecated Scripts (Do Not Use for Monthly Publishing)

The monthly workflow is:
- `publish_content_item.py` (single item)
- `publish_batch.py` (batch)

The scripts listed below were created during troubleshooting and **can reintroduce duplication/drift** if used on new content.
They are kept for reference only.

If you *must* run one, set `ALLOW_DEPRECATED_SCRIPTS=1` in your environment.

## Where they live now / how to run

Legacy scripts are now stored under `scripts/legacy/`.

To run one safely (from repo root), use module mode:

```bash
python -m scripts.legacy.fix_blog_block_issues
```

## Deprecated (legacy fix scripts)

- TOC / heading fixes:
  - `scripts/legacy/add_table_of_contents.py`
  - `scripts/legacy/add_toc_properly.py`
  - `scripts/legacy/fix_all_heading_ids.py`
  - `scripts/legacy/update_table_of_contents_complete.py`
  - `scripts/legacy/fix_duplicate_tocs.py`
  - `scripts/legacy/fix_duplicate_tocs_aggressive.py`
  - `scripts/legacy/fix_toc_final.py`
  - `scripts/legacy/create_clean_toc_post.py`
  - `scripts/legacy/create_clean_post_from_source.py`
  - `scripts/legacy/create_clean_post_final.py` (keep as reference; pipeline now handles TOC)

- FAQ repair scripts:
  - `scripts/legacy/convert_faq_to_schema_blocks.py`
  - `scripts/legacy/fix_faq_blocks_properly.py`
  - `scripts/legacy/fix_faq_simple_visible.py`
  - `scripts/legacy/fix_faq_remove_duplicates.py`
  - `scripts/legacy/fix_faq_visible_structure.py`
  - `scripts/legacy/fix_everything_you_need_faq.py`

- Blog layout/image patchers:
  - `scripts/legacy/add_content_images_to_blogs.py`
  - `scripts/legacy/fix_blog_image_alignment_and_faq.py`
  - `scripts/legacy/fix_blog_block_issues.py`
  - `scripts/legacy/update_blog_post_spacing.py`
  - `scripts/legacy/update_blog_featured_images.py`

## Why deprecated?

- They operate on **existing WordPress HTML state** (patching) instead of rebuilding from source.
- They may not be fully idempotent.
- They address narrow issues but don’t enforce the full “90% correct on first publish” rule set.

