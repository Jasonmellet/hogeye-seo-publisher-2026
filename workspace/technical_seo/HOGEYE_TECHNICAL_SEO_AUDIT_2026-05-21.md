# HogEye Technical SEO Audit

**Prepared for:** Phil  
**Site:** [hogeyecameras.com](https://hogeyecameras.com/)  
**Audit date:** May 21, 2026  
**Prepared by:** All Great Things  
**Evidence crawl ID:** `2026.05.21.07.33.25-agt-hogeye`  
**Method:** Full-site Screaming Frog crawl (198 URLs, production only)

---

## Executive summary

**Overall risk: High**

hogeyecameras.com has **active technical SEO debt that is getting worse, not better.** A full crawl on May 21, 2026 found **38 distinct issue classes** across the site. Several are **critical**: broken internal URLs, insecure HTTP resources on HTTPS pages, and structural metadata failures on roughly **half of all indexable HTML pages**.

This is not a hypothetical or checklist exercise. The same issue classes were documented in an April 2026 baseline audit. **Six weeks later, headline counts have increased** on broken links, mixed content, missing meta descriptions, and missing H1 headings — while the site has added new pages and new content is queued for publication.

**Bottom line:** Publishing more SEO content on this foundation risks wasted crawl budget, diluted rankings, browser trust warnings, and underperformance on the pages that matter most — including `/buy-now/`.

We recommend a **structured technical remediation program** before the next content batch goes live on WordPress.

---

## Site health at a glance

| Metric | April 2026 baseline | May 21, 2026 | Trend |
| --- | ---: | ---: | --- |
| Internal URLs discovered | 126 | 168 | Site grew (+33%) |
| HTML pages (2xx) | 19 | 34 | Content expanded (+79%) |
| Internal client errors (4xx) | 4 | **6** | **Worse (+50%)** |
| Mixed content instances | 19 | **34** | **Worse (+79%)** |
| HTTP URLs (should be HTTPS) | 19 | **19** | **Unchanged — still unresolved** |
| Missing meta descriptions (HTML) | 3 | **8** | **Worse (+167%)** |
| Missing H1 (HTML) | 12 | **17** | **Worse (+42%)** |
| Non-indexable internal URLs | — | 6 | Active indexation risk |

**Interpretation:** The site is scaling content and URL surface area **faster than its technical foundation is being maintained.** New pages are inheriting the same template, media, and metadata problems — which is why issue counts are rising in absolute terms.

---

## Critical findings (fix before scaling content)

### 1. Broken internal links — 6 client errors (High)

**What we found:** Six internal URLs return 4xx client errors (404 and related). These are live links on a production e-commerce and content site.

**Known examples from prior audit (still unresolved):**

| URL | Issue |
| --- | --- |
| `http://hogeyecameras.com/resources` | HTTP + 404 — dead resources hub |
| `https://hogeyecameras.com/sim-card-performance-for-ranch-cameras-lte-vs-multi-carrier/` | 404 |
| `https://hogeyecameras.com/trap-camera/` | 404 |
| `https://hogeyecameras.com/reolink-trap-mods-vs-hogeye-2026/` | 404 |

**Why it matters:**

- Google wastes crawl budget on dead ends instead of product and blog pages.
- Internal links to 404s leak PageRank and confuse site architecture.
- Users hitting broken links from navigation or older posts bounce — especially damaging on a high-consideration purchase path.

**Business impact:** Every new article that links into the site graph can **propagate broken paths** until redirects or content restoration are in place.

---

### 2. Mixed content — 34 instances across ~20% of internal URLs (High)

**What we found:** 34 instances where HTTPS pages load resources (images, scripts, CSS, PDFs) over insecure HTTP connections.

**Why it matters:**

- Modern browsers flag affected pages as **partially insecure** — a trust problem for a camera/security product brand.
- Mixed content can block resource loading entirely, breaking layouts and conversion elements.
- Google treats HTTPS as a baseline quality signal; persistent mixed content signals neglect.

**Trend:** Mixed content count **increased from 19 to 34** since April — strongly suggesting new content and media uploads are **adding HTTP asset references**, not fixing legacy ones.

**Likely root cause:** HTTP URLs embedded in the WordPress media library, Beaver Builder modules, or PDF/download links — not a one-off page fix.

---

### 3. HTTP URLs sitewide — 19 unresolved (High)

**What we found:** 19 internal URLs still use `http://` instead of `https://`.

**Why it matters:**

- Browsers display **"Not Secure"** warnings on HTTP pages.
- Creates redirect chains and duplicate URL variants search engines must reconcile.
- Often the same underlying problem as mixed content (legacy media and link references).

**Trend:** Count is **unchanged since April** — this has been sitting open for six weeks.

---

## High-impact on-page failures

### 4. Missing H1 headings — 17 of 34 HTML pages (50%) (Medium–High)

**What we found:** Half of all indexable HTML pages have **no detectable H1** (or empty/whitespace H1). An additional 17 pages have **multiple H1 tags** — a template-level pattern, not isolated typos.

**Pages of concern include `/buy-now/`** — the primary conversion URL.

**Why it matters:**

- H1 is one of the strongest on-page relevance signals; missing H1 tells Google and users what the page is about **less clearly than competitors**.
- Duplicate/multiple H1s across Beaver Builder layouts suggest **template debt**, meaning every new landing page may ship broken by default.

**Trend:** Missing H1 rose from **12 → 17** pages as the HTML footprint grew.

---

### 5. Missing meta descriptions — 8 of 34 HTML pages (24%) (Medium)

**What we found:** Eight indexable pages have no meta description — including category hub pages that should capture informational search demand.

**Why it matters:**

- Meta descriptions influence click-through rate in search results; missing descriptions mean Google **writes its own snippet** — often generic and uncompetitive.
- Category hubs (`/category/feral-hog-monitoring/` and siblings) are strategic entry points for the content program.

**Trend:** Missing meta rose from **3 → 8** since April.

---

### 6. Buy Now page — conversion page under-optimized (High)

**What we found (from April audit + May crawl confirmation):**

| Element | Status |
| --- | --- |
| Visible H1 | Missing |
| Title tag | Below 30 characters — too short to compete |
| Template | Likely Beaver Builder — heading structure not parsing cleanly |

**Why it matters:** This is not a blog post. It is the **primary revenue URL.** Technical and on-page gaps here directly affect paid and organic conversion efficiency.

---

### 7. Missing canonical tags — 5 pages (Medium)

**What we found:** Five HTML/PDF pages lack a canonical URL declaration.

**Why it matters:** Without canonicals, Google chooses its own preferred URL when duplicates or parameter variants exist — creating **ranking unpredictability** on pages you intend to rank.

---

## Secondary issues (still worth fixing in a structured pass)

| Issue | Count | Priority | Notes |
| --- | ---: | --- | --- |
| Images over 100 kB | 40 of 62 | Medium | Page speed / Core Web Vitals drag |
| Images missing size attributes | 18 | Low–Medium | Layout shift (CLS) risk |
| Images missing alt text | 4 | Medium | Accessibility + image search |
| Duplicate page titles | 2 | Medium | Indexation confusion |
| Page titles over pixel limit | 7 | Low–Medium | SERP truncation |
| Low content pages | 4 | Medium | Thin pages struggle to rank |
| Internal links with no anchor text | 34 pages | Low | Weak internal linking signal |
| Protocol-relative resource links | 5 | Low | Legacy anti-pattern |
| Security headers (HSTS, CSP, etc.) | 144–162 URLs | Low (for SEO sprint) | Hosting/server configuration — separate from content fixes |

These are real, but **secondary to the critical block** above. Fixing headers without fixing mixed content and 404s would not move the needle on search performance.

---

## What this means for the June content program

Five articles are in client review (Google Doc) and queued for WordPress publication. **Publishing them on the current site state carries avoidable risk:**

1. **New posts will link into a site graph that still contains 404s and HTTP assets** — passing equity to broken or insecure URLs.
2. **Template-level H1 and meta gaps will likely affect new posts the same way existing posts are affected** — unless templates are fixed first.
3. **Mixed content is accelerating** — each new post with media is another chance to embed HTTP references unless media workflow is corrected.
4. **ROI on content investment is capped** until crawlability, trust signals, and on-page structure are remediated.

**Recommendation:** Run a **technical fix sprint (Phase 1)** in parallel with or immediately before WordPress publication of the June batch — not after.

---

## Recommended remediation program

We recommend a **three-phase engagement** scoped to measurable outcomes, with verification crawls after each phase.

### Phase 1 — Stop the bleeding (1–2 weeks)

**Goal:** Restore crawlability and HTTPS trust.

| Work item | Expected outcome |
| --- | --- |
| Resolve 6 internal 4xx errors (redirect or restore) | Zero internal client errors on verification crawl |
| Replace HTTP asset and PDF links with HTTPS sitewide | HTTP URL count → 0; mixed content materially reduced |
| Fix `/buy-now/` H1 + title tag | Conversion page passes on-page baseline |

**Verification:** Focused URL-list crawl on affected URLs, then full re-crawl.

### Phase 2 — Template and metadata foundation (1–2 weeks)

**Goal:** Fix the patterns causing 50% missing H1 and 24% missing meta.

| Work item | Expected outcome |
| --- | --- |
| Category hub meta descriptions | All strategic hubs have unique meta |
| Beaver Builder / theme H1 structure | Single, visible H1 per HTML template |
| Missing canonicals (5 pages) | Canonical present on all indexable HTML |
| Image alt text (4 images) | Accessibility baseline met |

**Verification:** Full crawl + rendered HTML check on template pages.

### Phase 3 — Performance and polish (optional, 1 week)

**Goal:** Speed and SERP presentation.

| Work item | Expected outcome |
| --- | --- |
| Image compression / sizing (40 images >100 kB) | Reduced payload on key landing pages |
| Title/meta pixel-length cleanup | Improved SERP snippet control |
| Internal anchor text audit | Stronger internal linking graph |

**Verification:** Full crawl comparison logged against May 21 baseline.

---

## Risk if no action is taken

| Risk | Likelihood | Impact |
| --- | --- | --- |
| New content underperforms due to site-wide technical debt | High | High |
| Continued mixed content / browser warnings on product pages | High | Medium–High |
| Crawl budget wasted on 404s and non-indexable URLs | Medium | Medium |
| Competitors with cleaner technical foundations outrank on same keywords | Medium | High |
| June content investment fails to compound (each article starts from a weak base) | High | High |

---

## Evidence and reproducibility

All findings in this report are derived from Screaming Frog crawl exports stored in this repo:

```
work/seo/screaming_frog/2026.05.21.07.33.25-agt-hogeye/
├── crawl_overview.csv
├── issues_overview_report.csv
└── crawl_export.dbseospider
```

Comparison log: `workspace/technical_seo/CRAWL_COMPARISON.md`  
Issue queue (internal): `workspace/technical_seo/TRACKER.csv`  
April baseline reference: `workspace/technical_seo/BASELINE.md`

Crawl can be re-run and verified at any time using the same methodology.

---

## Next step

We recommend scheduling a **30-minute review** to walk through this audit, confirm priority order, and scope Phase 1 remediation. Phase 1 alone would materially reduce the highest-severity risks before the June articles go live.

**Contact:** jason@allgreatthings.io

---

*This audit reflects crawl evidence as of May 21, 2026. Counts may shift slightly on re-crawl; issue classes and root-cause patterns are stable until remediated.*
