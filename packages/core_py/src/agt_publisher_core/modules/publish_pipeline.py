"""
Canonical publishing pipeline (the one you should use every month).

Goals:
- 90% correct on first publish by enforcing:
  - rebuild-from-source
  - idempotent transforms (spacing, TOC)
  - media rules (featured != first body, unique-ish images)
  - post-update verification gates (FAQ count, image count, placeholders)

This intentionally replaces ad-hoc flows in older scripts.
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from agt_publisher_core.client_config import ClientConfig
from agt_publisher_core.modules.acf_blocks import build_acf_page_content
from agt_publisher_core.modules.links import InternalLinkManager
from agt_publisher_core.modules.metadata import MetadataHandler
from agt_publisher_core.modules.source_loader import load_content_file
from agt_publisher_core.modules.transforms import (
    add_spacing_to_html,
    ensure_unique_heading_ids,
    fix_malformed_h2_styles,
    insert_toc_after_intro,
    normalize_whitespace,
    remove_all_tocs,
)
from agt_publisher_core.modules.validators import ValidationResult, validate_blog_post, validate_landing_page
from agt_publisher_core.modules.wp_client import WordPressClient
from agt_publisher_core.config import Config


@dataclass(frozen=True)
class PublishOptions:
    # Common
    status: str = "draft"  # always default to draft
    resolve_links: bool = False
    # Opt-in only: overwrite an existing WP post/page for this exact URL/id.
    # Default monthly flow creates a NEW draft (unique slug if collision).
    allow_update_existing: bool = False

    # Blog-specific
    enable_toc: bool = False
    toc_auto_word_threshold: int = 1500
    # Mandate default: never auto-insert images (featured or in-body).
    min_content_images: int = 0
    max_content_images: int = 0
    # If set, enforce EXACT visible FAQ question count. If None, do not enforce.
    required_faq_questions: Optional[int] = None

    # Landing-page-specific
    use_acf_blocks: bool = True
    acf_large_image_search: str = "camp"
    acf_two_col_search: Optional[str] = None


class MediaMatcher:
    """
    Find relevant images in WP media library using keyword search + scoring.
    """

    def __init__(self, wp: WordPressClient):
        self.wp = wp

    def _score(self, media_item: Dict[str, Any], keywords: Sequence[str]) -> int:
        title = (media_item.get("title", {}) or {}).get("rendered", "") or ""
        alt = media_item.get("alt_text", "") or ""
        caption = (media_item.get("caption", {}) or {}).get("rendered", "") or ""
        hay = (title + " " + alt + " " + caption).lower()
        score = 0
        for kw in keywords:
            if kw and kw.lower() in hay:
                score += 1
        return score

    def find_best_media_ids(
        self,
        keywords: Sequence[str],
        *,
        exclude_ids: Optional[Sequence[int]] = None,
        limit: int = 5,
    ) -> List[int]:
        exclude = set(exclude_ids or [])
        candidates: Dict[int, int] = {}

        # Use WP search endpoint for multiple query terms; merge results.
        for kw in [k for k in keywords if k]:
            r = self.wp.get_json("media", params={"search": kw, "per_page": 20})
            if not r.ok or not isinstance(r.data, list):
                continue
            for item in r.data:
                mid = int(item.get("id", 0) or 0)
                if not mid or mid in exclude:
                    continue
                candidates[mid] = max(candidates.get(mid, 0), self._score(item, keywords))

        # If WP search returns nothing, fall back to latest media (first pages)
        if not candidates:
            r = self.wp.get_json("media", params={"per_page": 50})
            if r.ok and isinstance(r.data, list):
                for item in r.data:
                    mid = int(item.get("id", 0) or 0)
                    if not mid or mid in exclude:
                        continue
                    candidates[mid] = self._score(item, keywords)

        sorted_ids = [mid for mid, _ in sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)]
        return sorted_ids[:limit]

    def get_media_url_and_alt(self, media_id: int) -> Tuple[Optional[str], str]:
        r = self.wp.get_json(f"media/{media_id}")
        if not r.ok or not isinstance(r.data, dict):
            return None, ""
        url = r.data.get("source_url")
        alt = r.data.get("alt_text") or (r.data.get("title", {}) or {}).get("rendered", "") or ""
        return url, alt


class TaxonomyManager:
    def __init__(self, wp: WordPressClient):
        self.wp = wp
        self._category_cache: Dict[str, int] = {}
        self._tag_cache: Dict[str, int] = {}

    @staticmethod
    def _norm_name(name: str) -> str:
        # WP may return HTML entities in term names (&amp;).
        return html.unescape((name or "").strip()).lower()

    def _get_or_create(self, endpoint: str, name: str, cache: Dict[str, int]) -> Optional[int]:
        key = self._norm_name(name)
        if not key:
            return None
        if key in cache:
            return cache[key]

        def _match_in(items: Any) -> Optional[int]:
            if not isinstance(items, list):
                return None
            for item in items:
                if self._norm_name(item.get("name") or "") == key:
                    cid = int(item.get("id") or 0)
                    if cid:
                        cache[key] = cid
                        return cid
            return None

        # Search existing (compare unescaped names — WP may return &amp;)
        r = self.wp.get_json(endpoint, params={"search": name, "per_page": 100})
        hit = _match_in(r.data) if r.ok else None
        if hit:
            return hit

        # Fallback: list page (search can miss entity-encoded names)
        r_all = self.wp.get_json(endpoint, params={"per_page": 100, "hide_empty": False})
        hit = _match_in(r_all.data) if r_all.ok else None
        if hit:
            return hit

        # Create
        r2 = self.wp.post_json(endpoint, {"name": html.unescape(name.strip())})
        if r2.ok and isinstance(r2.data, dict):
            cid = int(r2.data.get("id") or 0)
            if cid:
                cache[key] = cid
                return cid

        # term_exists / race: list again
        r3 = self.wp.get_json(endpoint, params={"per_page": 100, "hide_empty": False})
        return _match_in(r3.data) if r3.ok else None

    def get_or_create_category_id(self, name: str) -> Optional[int]:
        return self._get_or_create("categories", name, self._category_cache)

    def get_or_create_tag_id(self, name: str) -> Optional[int]:
        return self._get_or_create("tags", name, self._tag_cache)


def _keyword_seed(item: Dict[str, Any]) -> List[str]:
    kws: List[str] = []
    title = item.get("title") or ""
    slug = item.get("slug") or ""
    kws.extend(re.split(r"[\s\-]+", str(title)))
    kws.extend(re.split(r"[\s\-]+", str(slug)))
    for k in item.get("_target_keywords", []) or []:
        kws.extend(re.split(r"[\s\-]+", str(k)))
    for t in item.get("tags", []) or []:
        kws.extend(re.split(r"[\s\-]+", str(t)))
    # Keep short list of meaningful words
    kws = [k.strip().lower() for k in kws if k and len(k.strip()) >= 4]
    # De-dupe preserving order
    seen = set()
    out = []
    for k in kws:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out[:12]


def _create_wp_image_block(url: str, alt: str, media_id: int) -> str:
    return (
        f'<!-- wp:image {{"align":"full","width":600,"height":400}} -->\n'
        f'<figure class="wp-block-image alignfull" style="width:100%; max-width:100%">'
        f'<img src="{url}" alt="{alt}" class="wp-image-{media_id}" style="max-width:100%; height:auto; border-radius:8px;"/>'
        f"</figure>\n"
        f"<!-- /wp:image -->"
    )


def _insert_images_blog(content: str, media: MediaMatcher, image_ids: List[int]) -> str:
    """
    Insert images at natural break points (after intro and after later H2s).
    """
    if not image_ids:
        return content

    # Build blocks
    blocks: List[str] = []
    for mid in image_ids:
        url, alt = media.get_media_url_and_alt(mid)
        if not url:
            continue
        blocks.append(_create_wp_image_block(url, alt, mid))
    if not blocks:
        return content

    # Insert after second paragraph
    paras = list(re.finditer(r"(<p[^>]*>.*?</p>)", content, flags=re.IGNORECASE | re.DOTALL))
    updated = content
    inserted = 0
    if len(paras) >= 2 and inserted < len(blocks):
        pos = paras[1].end()
        updated = updated[:pos] + "\n\n" + blocks[inserted] + "\n\n" + updated[pos:]
        inserted += 1

    # Insert after H2 #2 and H2 #4 (if available)
    h2s = list(re.finditer(r"(<h2[^>]*>.*?</h2>)", updated, flags=re.IGNORECASE | re.DOTALL))
    for target_idx in [1, 3]:
        if inserted >= len(blocks):
            break
        if target_idx < len(h2s):
            pos = h2s[target_idx].end()
            # avoid placing an image immediately adjacent to another image
            nearby = updated[max(0, pos - 400) : min(len(updated), pos + 400)]
            if "wp-image-" in nearby:
                continue
            updated = updated[:pos] + "\n\n" + blocks[inserted] + "\n\n" + updated[pos:]
            inserted += 1

    return updated


class PublishPipeline:
    def __init__(
        self,
        session,
        *,
        client: Optional[ClientConfig] = None,
    ):
        self.wp = WordPressClient(session)
        self.media = MediaMatcher(self.wp)
        self.meta = MetadataHandler()
        self.links = InternalLinkManager(session, link_aliases=(client.linkAliases if client else None))
        self.tax = TaxonomyManager(self.wp)
        self.client = client

    def _seo_plugin(self) -> str:
        if self.client and self.client.seoPlugin:
            return str(self.client.seoPlugin)
        # HogEye / WD default stack is AIOSEO. Never soft-fail as Yoast by accident.
        return "aioseo"

    def _auto_images_enabled(self) -> bool:
        # Mandate: never auto-insert images unless client.config explicitly opts in.
        if self.client and self.client.autoInsertImages is not None:
            return bool(self.client.autoInsertImages)
        return False

    def _seo_field_warnings(self, item: Dict[str, Any]) -> List[str]:
        """Soft reminders only when SEO hard-fail is not already gating (unused for AIOSEO path)."""
        return []

    def _aioseo_required_errors(self, item: Dict[str, Any]) -> List[str]:
        """Hard-fail missing SEO meta — body-only publish is a failed publish (hub Draft-first)."""
        out: List[str] = []
        if not (str(item.get("meta_title") or "").strip()):
            out.append("SEO hard-fail: meta_title is empty (SEO title required).")
        if not (str(item.get("meta_description") or "").strip()):
            out.append("SEO hard-fail: meta_description is empty (meta description required).")
        if not (str(item.get("focus_keyword") or "").strip()):
            out.append("SEO hard-fail: focus_keyword is empty (focus keyphrase required).")
        return out

    @staticmethod
    def _update_existing_allowed(item: Dict[str, Any], *, options: PublishOptions) -> bool:
        """Create-only by default. Stored wp_post_id / wp_page_id alone is NOT opt-in
        (leftover ids must not silently overwrite). Require CLI --allow-update-existing
        or JSON update_existing / _update_existing == true. Ids then target the update.
        """
        if options.allow_update_existing:
            return True
        if item.get("update_existing") is True or item.get("_update_existing") is True:
            return True
        return False

    def _slug_collision(
        self, slug: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Return (existing_post, existing_page) for slug across any status."""
        if not slug:
            return None, None
        post_exists, post = self.wp.find_by_slug("posts", slug)
        page_exists, page = self.wp.find_by_slug("pages", slug)
        return (post if post_exists else None), (page if page_exists else None)

    def _allocate_unique_slug(self, base_slug: str, *, period: Optional[str]) -> str:
        """Prefer …-YYYY-MM-refresh, then numeric suffixes, until free on posts and pages."""
        period_token = None
        if isinstance(period, str) and re.match(r"^\d{4}-\d{2}$", period.strip()):
            period_token = period.strip()
        candidates = []
        if period_token:
            candidates.append(f"{base_slug}-{period_token}-refresh")
        candidates.append(f"{base_slug}-refresh")
        for n in range(2, 50):
            candidates.append(f"{base_slug}-refresh-{n}")
        for candidate in candidates:
            post, page = self._slug_collision(candidate)
            if not post and not page:
                return candidate
        raise ValueError(f"Could not allocate a unique slug from base '{base_slug}'.")

    def _backup_wp_object(self, endpoint: str, object_id: int, slug: str) -> None:
        """
        Save a local JSON backup of the WP object prior to mutation.
        This is a safety net beyond WordPress daily backups and helps debugging diffs.
        """
        try:
            r = self.wp.get_json(f"{endpoint}/{object_id}", params={"context": "edit"})
            if not r.ok or not isinstance(r.data, dict):
                return
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            safe_slug = re.sub(r"[^a-zA-Z0-9\-_]+", "_", slug or str(object_id))
            out_dir = os.path.join("work", "wp_backups")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{endpoint}_{safe_slug}_{object_id}_{ts}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(r.data, f, ensure_ascii=False, indent=2)
        except Exception:
            # Backups are best-effort; never block publishing.
            return

    @staticmethod
    def _content_raw_or_rendered(obj: Dict[str, Any]) -> str:
        c = obj.get("content") or {}
        if isinstance(c, dict):
            return (c.get("raw") or c.get("rendered") or "") or ""
        return ""

    @staticmethod
    def _enforce_preserve_markers(existing_content: str, updated_content: str, markers: Sequence[str]) -> Optional[str]:
        """
        Ensure any critical markers present in the existing page remain present after update.
        Returns an error message if a marker would be removed.
        """
        ex = existing_content.lower()
        up = updated_content.lower()
        for m in markers:
            if m.lower() in ex and m.lower() not in up:
                return f"Safety stop: would remove protected marker '{m}'. Add it to the source content or disable the update for this page."
        return None

    def publish_from_file(
        self,
        source_path: str,
        *,
        content_type: Optional[str] = None,
        options: PublishOptions = PublishOptions(),
    ) -> Tuple[Optional[int], ValidationResult]:
        loaded = load_content_file(source_path)
        item = loaded.data

        inferred_type = content_type
        if inferred_type is None:
            # Infer from path
            if "/content/pages/" in source_path.replace("\\", "/"):
                inferred_type = "pages"
            else:
                inferred_type = "posts"

        if inferred_type not in ["posts", "pages"]:
            raise ValueError("content_type must be 'posts' or 'pages'")

        if inferred_type == "posts":
            return self._publish_post(item, options=options)
        return self._publish_page(item, options=options)

    def _publish_post(self, item: Dict[str, Any], *, options: PublishOptions) -> Tuple[Optional[int], ValidationResult]:
        slug = (item.get("slug") or "").strip()
        title = item.get("title", "")
        raw_content = (item.get("content") or "").replace("\\n", "\n")
        notes: List[str] = []

        seo_errors = self._aioseo_required_errors(item)
        if seo_errors:
            return None, ValidationResult(ok=False, errors=seo_errors, warnings=[])

        cat_names = [str(c).strip() for c in (item.get("categories") or []) if str(c).strip()]
        if item.get("wp_category_id"):
            pass  # explicit id allowed
        elif not cat_names:
            return None, ValidationResult(
                ok=False,
                errors=["Category hard-fail: assign a real WP category (never leave Uncategorized)."],
                warnings=[],
            )
        elif any(c.lower() == "uncategorized" for c in cat_names):
            return None, ValidationResult(
                ok=False,
                errors=["Category hard-fail: Uncategorized is not allowed."],
                warnings=[],
            )

        # Transform content safely
        content = fix_malformed_h2_styles(raw_content)
        content = add_spacing_to_html(content)
        content = normalize_whitespace(content)

        # TOC (auto or enabled)
        word_count = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", content)))
        enable_toc = options.enable_toc or word_count >= options.toc_auto_word_threshold or bool(item.get("enable_toc"))
        if enable_toc:
            content = remove_all_tocs(content)
            content, _ = ensure_unique_heading_ids(content)
            content, _ = insert_toc_after_intro(content)

        # Links (optional; if not resolving, we keep placeholders but validator will warn)
        slug_map: Optional[Dict[str, str]] = None
        if options.resolve_links:
            slug_map = self.links.build_slug_map()
            content = self.links.replace_link_placeholders(content, slug_map)

        # FAQ schema text (AIOSEO) may still contain {{link:...}}; resolve to real URLs when present
        faq_rows = item.get("faq_items")
        if isinstance(faq_rows, list) and faq_rows:
            need_faq_links = any(
                isinstance(r, dict) and "{{link:" in str(r.get("question", "")) + str(r.get("answer", ""))
                for r in faq_rows
            )
            if need_faq_links:
                if slug_map is None:
                    slug_map = self.links.build_slug_map()
                for row in faq_rows:
                    if not isinstance(row, dict):
                        continue
                    for key in ("question", "answer"):
                        v = row.get(key)
                        if isinstance(v, str) and "{{link:" in v:
                            row[key] = self.links.replace_link_placeholders(v, slug_map)

        # Images only when client.config autoInsertImages=true AND CLI budgets allow it.
        auto_images_enabled = (
            self._auto_images_enabled()
            and (options.max_content_images > 0 or bool(item.get("featured_media_id")) or bool(item.get("content_image_count")))
        )
        min_content_images_required = options.min_content_images if auto_images_enabled else 0

        # Featured image selection (opt-in only)
        featured_media_id = int(item.get("featured_media_id") or 0)
        if auto_images_enabled and not featured_media_id:
            seed = _keyword_seed(item)
            best = self.media.find_best_media_ids(seed, exclude_ids=[], limit=1)
            featured_media_id = best[0] if best else 0

        # Ensure featured image not in body: replace the first occurrence if present
        if auto_images_enabled and featured_media_id and f"wp-image-{featured_media_id}" in content:
            seed = _keyword_seed(item)
            alt_ids = self.media.find_best_media_ids(seed, exclude_ids=[featured_media_id], limit=3)
            replacement_id = alt_ids[0] if alt_ids else 0
            if replacement_id:
                url, alt = self.media.get_media_url_and_alt(replacement_id)
                if url:
                    content = re.sub(
                        rf"(wp-image-){featured_media_id}",
                        rf"\g<1>{replacement_id}",
                        content,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                    content = re.sub(
                        rf'(<img[^>]+class="[^"]*wp-image-{replacement_id}[^"]*"[^>]+src=")[^"]+(")',
                        rf"\g<1>{url}\2",
                        content,
                        count=1,
                        flags=re.IGNORECASE,
                    )

        # Insert body images only when auto-images is explicitly enabled and budgets > 0
        if auto_images_enabled and options.max_content_images > 0:
            desired = int(item.get("content_image_count") or options.max_content_images)
            desired = max(options.min_content_images, min(desired, options.max_content_images))
            existing_body_ids = set([int(x) for x in re.findall(r"wp-image-(\d+)", content)])
            needed = max(0, desired - len(existing_body_ids))
            if needed > 0:
                seed = _keyword_seed(item)
                candidates = self.media.find_best_media_ids(
                    seed,
                    exclude_ids=list(existing_body_ids) + ([featured_media_id] if featured_media_id else []),
                    limit=needed + 2,
                )
                content = _insert_images_blog(content, self.media, candidates[:needed])

        # Slug collision policy (posts OR pages, any status)
        allow_update = self._update_existing_allowed(item, options=options)
        existing_post, existing_page = self._slug_collision(slug) if slug else (None, None)
        target_post_id: Optional[int] = None
        if allow_update:
            if item.get("wp_post_id"):
                target_post_id = int(item["wp_post_id"])
            elif existing_post and existing_post.get("id"):
                target_post_id = int(existing_post["id"])
            elif existing_page and existing_page.get("id") and not item.get("wp_page_id"):
                return None, ValidationResult(
                    ok=False,
                    errors=[
                        f"Slug '{slug}' matches an existing PAGE (id={existing_page.get('id')}). "
                        "Refusing to overwrite a page from the posts publisher without wp_page_id / intentional page workflow."
                    ],
                    warnings=[],
                )
        else:
            if existing_post or existing_page:
                kind = "post" if existing_post else "page"
                hit = existing_post or existing_page or {}
                period = item.get("period") or item.get("month")
                if not period:
                    # Filename convention: jul26_01_… → 2026-07
                    ext = str(item.get("externalId") or item.get("external_id") or "")
                    m = re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{2})", ext.lower())
                    months = {
                        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
                        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
                    }
                    if m and m.group(1) in months:
                        period = f"20{m.group(2)}-{months[m.group(1)]}"
                new_slug = self._allocate_unique_slug(slug, period=str(period) if period else None)
                notes.append(
                    f"Slug '{slug}' already exists as {kind} id={hit.get('id')}; "
                    f"creating NEW draft as '{new_slug}' (pass --allow-update-existing to overwrite intentionally)."
                )
                slug = new_slug

        # Final payload
        payload: Dict[str, Any] = {
            "title": title,
            "slug": slug,
            "status": options.status,
            "content": content,
            "excerpt": item.get("excerpt", "") or "",
        }
        payload.update(self.meta.seo_rest_fields(item, plugin=self._seo_plugin()))

        # Categories/tags (names in source -> IDs in WP)
        cat_ids: List[int] = []
        if item.get("wp_category_id"):
            try:
                cat_ids.append(int(item["wp_category_id"]))
            except (TypeError, ValueError):
                return None, ValidationResult(ok=False, errors=["Invalid wp_category_id"], warnings=[])
        for cat_name in cat_names:
            cid = self.tax.get_or_create_category_id(cat_name)
            if cid:
                cat_ids.append(cid)
        seen_cats: set[int] = set()
        deduped_cats: List[int] = []
        for cid in cat_ids:
            if cid in seen_cats:
                continue
            seen_cats.add(cid)
            deduped_cats.append(cid)
        cat_ids = deduped_cats
        if not cat_ids:
            return None, ValidationResult(
                ok=False,
                errors=["Category hard-fail: could not resolve any WP category IDs."],
                warnings=[],
            )
        payload["categories"] = cat_ids

        tag_ids: List[int] = []
        for tag_name in item.get("tags", []) or []:
            tid = self.tax.get_or_create_tag_id(str(tag_name))
            if tid:
                tag_ids.append(tid)
        if tag_ids:
            payload["tags"] = tag_ids

        if item.get("date"):
            payload["date"] = item.get("date")
        # Mandate: do not set featured_media unless explicitly provided / auto-images opted in.
        if featured_media_id and (auto_images_enabled or item.get("featured_media_id")):
            payload["featured_media"] = featured_media_id
        else:
            featured_media_id = 0

        if Config.DRY_RUN:
            validation = validate_blog_post(
                content=content,
                featured_media_id=featured_media_id,
                min_content_images=min_content_images_required,
                max_content_images=options.max_content_images,
                required_faq_questions=options.required_faq_questions,
                require_featured_not_in_body=False if featured_media_id == 0 else True,
            )
            seo_w = self._seo_field_warnings(item)
            return None, ValidationResult(
                ok=validation.ok,
                errors=validation.errors,
                warnings=["DRY_RUN=true: skipped WordPress write (no post created/updated)."]
                + validation.warnings
                + seo_w
                + notes,
            )

        # Create new draft OR update only when explicitly allowed
        if target_post_id:
            self._backup_wp_object("posts", target_post_id, slug or str(target_post_id))
            r = self.wp.post_json(f"posts/{target_post_id}", payload, params={"context": "edit"})
            if not r.ok:
                return None, ValidationResult(ok=False, errors=[f"Failed updating post: HTTP {r.status_code}"], warnings=notes)
            post_id = target_post_id
            notes.append(f"Updated existing post id={post_id} (explicit allow-update).")
        else:
            r = self.wp.post_json("posts", payload, params={"context": "edit"})
            if not r.ok:
                return None, ValidationResult(ok=False, errors=[f"Failed creating post: HTTP {r.status_code}"], warnings=notes)
            post_id = int((r.data or {}).get("id") or 0)

        # Verify
        got = self.wp.get_json(f"posts/{post_id}", params={"context": "edit"})
        content_raw = ""
        featured = featured_media_id
        verify_errors: List[str] = []
        if got.ok and isinstance(got.data, dict):
            content_raw = ((got.data.get("content") or {}).get("raw") or (got.data.get("content") or {}).get("rendered") or "")
            featured = int(got.data.get("featured_media") or 0)
            status_got = (got.data.get("status") or "").strip()
            if options.status == "draft" and status_got and status_got != "draft":
                verify_errors.append(f"Expected status=draft, got status={status_got}.")
            cats_got = got.data.get("categories") or []
            if not cats_got:
                verify_errors.append("WP draft has no categories after publish.")
            aio = got.data.get("aioseo_meta_data") or {}
            if isinstance(aio, dict):
                if not str(aio.get("title") or "").strip():
                    verify_errors.append("AIOSEO verify hard-fail: title missing on WP draft.")
                if not str(aio.get("description") or "").strip():
                    verify_errors.append("AIOSEO verify hard-fail: description missing on WP draft.")
                focus = ((aio.get("keyphrases") or {}).get("focus") or {}) if isinstance(aio.get("keyphrases"), dict) else {}
                if not str((focus or {}).get("keyphrase") or "").strip():
                    verify_errors.append("AIOSEO verify hard-fail: focus keyphrase missing on WP draft.")
            else:
                verify_errors.append("AIOSEO verify hard-fail: aioseo_meta_data missing on WP draft.")
            if featured:
                verify_errors.append(f"featured_media={featured} but mandate requires 0 for this run (no auto images).")
            if re.search(r"wp-image-\d+", content_raw or content) and not re.search(
                r"wp-image-\d+", (item.get("content") or "")
            ):
                verify_errors.append("Body contains wp-image-* that was not in source (auto-insert suspected).")

        validation = validate_blog_post(
            content=content_raw or content,
            featured_media_id=featured,
            min_content_images=min_content_images_required,
            max_content_images=options.max_content_images,
            required_faq_questions=options.required_faq_questions,
            require_featured_not_in_body=False if featured == 0 else True,
        )
        seo_w = self._seo_field_warnings(item)
        errors = list(validation.errors) + verify_errors
        warnings = list(validation.warnings) + seo_w + notes
        ok = validation.ok and not verify_errors
        return post_id, ValidationResult(ok=ok, errors=errors, warnings=warnings)

    def _publish_page(self, item: Dict[str, Any], *, options: PublishOptions) -> Tuple[Optional[int], ValidationResult]:
        slug = item.get("slug", "")
        title = item.get("title", "")
        raw_content = (item.get("content") or "").replace("\\n", "\n")

        seo_errors = self._aioseo_required_errors(item)
        if seo_errors:
            return None, ValidationResult(ok=False, errors=seo_errors, warnings=[])

        # Existing page is required for our landing page workflow; also lets us avoid
        # duplicating the hero/featured image inside body image blocks.
        exists, existing = self.wp.find_by_slug("pages", slug) if slug else (False, None)
        if not exists or not existing or not existing.get("id"):
            # For landing pages we prefer update by slug; creating can break menus/SEO.
            return None, ValidationResult(ok=False, errors=[f"Page with slug '{slug}' not found. Create it first or use the proper workflow."], warnings=[])

        page_id = int(existing["id"])
        existing_featured_id = int(existing.get("featured_media") or 0)
        existing_content = self._content_raw_or_rendered(existing)

        # Local backup before mutation (safety net)
        self._backup_wp_object("pages", page_id, slug or str(page_id))

        # Transform content safely before block conversion
        content = add_spacing_to_html(raw_content)
        content = normalize_whitespace(content)

        # Links (optional): resolve {{link:...}} placeholders before ACF conversion
        if options.resolve_links:
            slug_map = self.links.build_slug_map()
            content = self.links.replace_link_placeholders(content, slug_map)

        # Decide ACF conversion (default is conservative; only auto-enable for interior-template pages)
        use_acf = False
        if "use_acf_blocks" in item:
            use_acf = bool(item.get("use_acf_blocks"))
        else:
            use_acf = bool(options.use_acf_blocks and (existing.get("template") or "") == "template-interior.php")

        # ACF blocks (only when explicitly enabled or safe-by-template)
        payload: Dict[str, Any]
        if use_acf:
            # Allow explicit image IDs in source content for deterministic, non-duplicative layout
            large_id = int(item.get("acf_large_image_id") or 0)
            two_col_ids = item.get("acf_two_col_image_ids") or item.get("acf_two_col_images") or None
            if isinstance(two_col_ids, list):
                two_col_ids = [int(x) for x in two_col_ids if str(x).isdigit()]
            else:
                two_col_ids = None

            if not large_id:
                seed = _keyword_seed(item)
                large_ids = self.media.find_best_media_ids(
                    [options.acf_large_image_search] + seed,
                    exclude_ids=[existing_featured_id] if existing_featured_id else None,
                    limit=5,
                )
                large_id = large_ids[0] if large_ids else 0

            # If someone explicitly set a large image that matches hero/featured, avoid duplication.
            if large_id and existing_featured_id and large_id == existing_featured_id:
                seed = _keyword_seed(item)
                alt_large = self.media.find_best_media_ids(
                    [options.acf_large_image_search] + seed,
                    exclude_ids=[existing_featured_id],
                    limit=5,
                )
                large_id = alt_large[0] if alt_large else large_id

            if not two_col_ids or len(two_col_ids) < 2:
                seed = _keyword_seed(item)
                two_ids = self.media.find_best_media_ids(
                    ([options.acf_two_col_search] if options.acf_two_col_search else []) + seed,
                    exclude_ids=[x for x in [large_id, existing_featured_id] if x],
                    limit=2,
                )
                two_col_ids = two_ids if len(two_ids) == 2 else None
            # Preserve existing template unless explicitly set in source
            template = item.get("template") or (existing.get("template") or None)
            acf_payload = build_acf_page_content(
                content,
                large_image_id=large_id or 0,
                two_col_image_ids=two_col_ids if (two_col_ids and len(two_col_ids) == 2) else None,
                template=template,
            )
            payload = {
                "title": title,
                "slug": slug,
                "status": options.status,
                "excerpt": item.get("excerpt", "") or "",
                **acf_payload,
            }
            payload.update(self.meta.seo_rest_fields(item, plugin=self._seo_plugin()))
        else:
            payload = {
                "title": title,
                "slug": slug,
                "status": options.status,
                "content": content,
                "excerpt": item.get("excerpt", "") or "",
            }
            payload.update(self.meta.seo_rest_fields(item, plugin=self._seo_plugin()))

        # Optional per-client protected markers by slug
        preserve_markers: List[str] = []
        if self.client and self.client.protectedMarkersBySlug:
            preserve_markers = list(self.client.protectedMarkersBySlug.get((slug or "").strip().lower(), []) or [])
        err = self._enforce_preserve_markers(existing_content, payload.get("content", "") or "", preserve_markers)
        if err:
            return None, ValidationResult(ok=False, errors=[err], warnings=[])

        if Config.DRY_RUN:
            host = (urlparse(Config.WP_SITE_URL).hostname or "").lower()
            validation = validate_landing_page(content=payload.get("content", "") or "", internal_link_host=host)
            seo_w = self._seo_field_warnings(item)
            return None, ValidationResult(
                ok=validation.ok,
                errors=validation.errors,
                warnings=["DRY_RUN=true: skipped WordPress write (no page updated)."] + validation.warnings + seo_w,
            )

        r = self.wp.post_json(f"pages/{page_id}", payload, params={"context": "edit"})
        if not r.ok:
            return None, ValidationResult(ok=False, errors=[f"Failed updating page: HTTP {r.status_code}"], warnings=[])

        # Verify (for ACF, validate the final content string; we check H2 count at minimum)
        got = self.wp.get_json(f"pages/{page_id}", params={"context": "edit"})
        content_raw = ""
        if got.ok and isinstance(got.data, dict):
            content_raw = ((got.data.get("content") or {}).get("raw") or (got.data.get("content") or {}).get("rendered") or "")

        host = (urlparse(Config.WP_SITE_URL).hostname or "").lower()
        validation = validate_landing_page(content=content_raw or payload.get("content", ""), internal_link_host=host)
        seo_w = self._seo_field_warnings(item)
        if not seo_w:
            return page_id, validation
        return page_id, ValidationResult(ok=validation.ok, errors=list(validation.errors), warnings=list(validation.warnings) + seo_w)

