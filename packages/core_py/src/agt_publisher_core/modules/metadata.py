"""
Metadata and Schema Module
Handles SEO metadata and schema markup
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional


def _aioseo_faqpage_graph(*, faq_items: List[Dict[str, str]], slug: str) -> Dict[str, Any]:
    """
    One AIOSEO schema graph entry (FAQPage), matching shapes seen in aioseo_meta_data.schema.graphs[].
    """
    suf = hashlib.md5((slug or "post").encode("utf-8")).hexdigest()[:10]
    questions: List[Dict[str, str]] = []
    for row in faq_items:
        q = (row.get("question") or "").strip()
        a = (row.get("answer") or "").strip()
        if not q or not a:
            continue
        questions.append({"question": q, "answer": a})
    if not questions:
        return {}
    return {
        "id": f"#aioseo-faq-page-{suf}",
        "slug": "faq-page",
        "graphName": "FAQPage",
        "label": "FAQ",
        "properties": {
            "name": "#post_title",
            "description": "",
            "questions": questions,
        },
        "value": "faq-page",
    }


def _aioseo_schema_wrapper_with_faq_graph(faq_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Minimal schema object so REST accepts FAQ without stripping default BlogPosting context."""
    empty_lists = {
        "Article": [],
        "Course": [],
        "Dataset": [],
        "FAQPage": [],
        "Movie": [],
        "Person": [],
        "Product": [],
        "ProductReview": [],
        "Car": [],
        "Recipe": [],
        "Service": [],
        "SoftwareApplication": [],
        "WebPage": [],
    }
    return {
        "blockGraphs": [],
        "customGraphs": [],
        "default": {
            "data": empty_lists,
            "graphName": "BlogPosting",
            "isEnabled": True,
        },
        "graphs": [faq_graph],
    }


class MetadataHandler:
    """Handle SEO metadata and schema markup"""

    def __init__(self):
        self.schema_templates = {}

    def generate_article_schema(self, post: Dict, site_info: Dict) -> str:
        """
        Generate Article schema (JSON-LD) for blog post
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.get("title", ""),
            "description": post.get("excerpt", ""),
        }

        # Add author if provided
        if post.get("author_name"):
            schema["author"] = {"@type": "Person", "name": post["author_name"]}

        # Add publisher if provided
        if site_info.get("site_name"):
            schema["publisher"] = {"@type": "Organization", "name": site_info["site_name"]}

        # Add image if provided
        if post.get("featured_image_url"):
            schema["image"] = post["featured_image_url"]

        # Add dates if provided
        if post.get("date_published"):
            schema["datePublished"] = post["date_published"]

        if post.get("date_modified"):
            schema["dateModified"] = post["date_modified"]

        return json.dumps(schema, indent=2)

    def generate_local_business_schema(self, business_info: Dict) -> str:
        """
        Generate LocalBusiness schema
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_info.get("name", "Camp Lakota"),
            "description": business_info.get("description", ""),
        }

        # Add address if provided
        if business_info.get("address"):
            addr = business_info["address"]
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": addr.get("street", ""),
                "addressLocality": addr.get("city", ""),
                "addressRegion": addr.get("state", ""),
                "postalCode": addr.get("zip", ""),
                "addressCountry": addr.get("country", "US"),
            }

        # Add contact info
        if business_info.get("phone"):
            schema["telephone"] = business_info["phone"]

        if business_info.get("email"):
            schema["email"] = business_info["email"]

        if business_info.get("website"):
            schema["url"] = business_info["website"]

        # Add logo
        if business_info.get("logo"):
            schema["logo"] = business_info["logo"]

        # Add image
        if business_info.get("image"):
            schema["image"] = business_info["image"]

        # Add opening hours if provided
        if business_info.get("opening_hours"):
            schema["openingHours"] = business_info["opening_hours"]

        # Add price range if provided
        if business_info.get("price_range"):
            schema["priceRange"] = business_info["price_range"]

        return json.dumps(schema, indent=2)

    def generate_organization_schema(self, org_info: Dict) -> str:
        """
        Generate Organization schema
        """
        schema = {"@context": "https://schema.org", "@type": "Organization", "name": org_info.get("name", "Camp Lakota"), "url": org_info.get("url", "")}

        if org_info.get("logo"):
            schema["logo"] = org_info["logo"]

        if org_info.get("description"):
            schema["description"] = org_info["description"]

        # Social media profiles
        if org_info.get("social_profiles"):
            schema["sameAs"] = org_info["social_profiles"]

        return json.dumps(schema, indent=2)

    def inject_schema_into_content(self, content: str, schema_json: str) -> str:
        """
        Inject schema markup into HTML content
        """
        schema_script = f'<script type="application/ld+json">\n{schema_json}\n</script>\n\n'
        return schema_script + content

    def prepare_yoast_meta(self, content: Dict) -> Dict:
        """
        Prepare meta fields for Yoast SEO plugin
        """
        meta = {}

        # Yoast expects these meta keys (with leading underscore) when updated via REST.
        if content.get("meta_title"):
            meta["_yoast_wpseo_title"] = content["meta_title"]

        if content.get("meta_description"):
            meta["_yoast_wpseo_metadesc"] = content["meta_description"]

        if content.get("focus_keyword"):
            meta["_yoast_wpseo_focuskw"] = content["focus_keyword"]

        return meta

    def prepare_rankmath_meta(self, content: Dict) -> Dict:
        """
        Prepare meta fields for Rank Math plugin
        """
        meta = {}

        if content.get("meta_title"):
            meta["rank_math_title"] = content["meta_title"]

        if content.get("meta_description"):
            meta["rank_math_description"] = content["meta_description"]

        if content.get("focus_keyword"):
            meta["rank_math_focus_keyword"] = content["focus_keyword"]

        return meta

    def prepare_aioseo_meta_data(self, content: Dict) -> Dict:
        """
        Minimal AIOSEO REST payload (requires AIOSEO REST API / compatible version).
        Maps content JSON keys to aioseo_meta_data on POST /wp/v2/posts|pages.

        Optional `faq_items`: [{"question": "...", "answer": "..."}, ...] → FAQPage graph in schema.graphs
        (shows in AIOSEO Schema / alongside Article BlogPosting).
        """
        out: Dict[str, Any] = {}
        if content.get("meta_title"):
            out["title"] = content["meta_title"]
        if content.get("meta_description"):
            out["description"] = content["meta_description"]
        if content.get("focus_keyword"):
            out["keyphrases"] = {"focus": {"keyphrase": content["focus_keyword"]}}

        raw_faq = content.get("faq_items")
        faq_list: Optional[List[Dict[str, str]]] = None
        if isinstance(raw_faq, list) and raw_faq:
            faq_list = []
            for row in raw_faq:
                if not isinstance(row, dict):
                    continue
                faq_list.append(
                    {
                        "question": str(row.get("question") or "").strip(),
                        "answer": str(row.get("answer") or "").strip(),
                    }
                )
            faq_list = [x for x in faq_list if x["question"] and x["answer"]]

        if faq_list:
            slug = str(content.get("slug") or "").strip()
            g = _aioseo_faqpage_graph(faq_items=faq_list, slug=slug)
            if g:
                out["schema"] = _aioseo_schema_wrapper_with_faq_graph(g)
                out["schema_type"] = "default"

        return out

    def seo_rest_fields(self, content: Dict, *, plugin: str = "yoast") -> Dict:
        """
        Top-level REST keys for the active SEO plugin (merge into wp/v2 payload).
        """
        p = (plugin or "yoast").strip().lower()
        if p == "aioseo":
            aio = self.prepare_aioseo_meta_data(content)
            return {"aioseo_meta_data": aio} if aio else {}
        if p == "rankmath":
            return {"meta": self.prepare_rankmath_meta(content)}
        return {"meta": self.prepare_yoast_meta(content)}

