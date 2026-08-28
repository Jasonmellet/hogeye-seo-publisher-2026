# Technical SEO & structural findings — HogEye Cameras

**Client:** HogEye Cameras (`hogeye`)  
**Document:** Technical SEO & structural findings  
**Created:** 2026-04-09  

**Analysis type:** Technical and on-page review from Screaming Frog exports.  
**Data location:** `clients/hogeye/inputs/screaming_frog/2026.04.09.05.15.26/`  
**Primary sources:** `internal_all.csv`, `response_codes_all.csv`, `page_titles_all.csv`, `meta_description_all.csv`, `h1_all.csv`, `h2_all.csv`, `canonicals_all.csv`, `directives_all.csv`, `issues_overview_report.csv`, `security` / PageSpeed exports as cited  
**Crawl timestamp (from export):** 2026-04-09  

---

## How to read this document

Rules applied: evidence-only review, impact-first prioritization (`prompts/system/analysis-guardrails.md`, `rubrics/technical-seo.md`).

**Client context:** WordPress marketing site (`https://hogeyecameras.com/`) — cellular / hog-trap / ranch camera positioning per `client_config.yaml`. **Google Search Console** exports are **not** available; prioritize fixes that remove crawl errors and security issues first, then snippets and headings.

---

## Crawl snapshot

| Metric | Value | Source |
| ------ | ----: | ------ |
| Rows in `internal_all.csv` | **126** | `internal_all.csv` |
| **HTML** URLs | **23** | `internal_all.csv` (`Content Type` contains `text/html`) |
| **Indexable + 200 + HTML** | **19** | `internal_all.csv` |
| **404** HTML responses | **4** | `response_codes_all.csv`, `internal_all.csv` |

**Sitewide scale:** Modest HTML surface area; several **issues** percentages in Screaming Frog are relative to **23** HTML URLs (see `% of Total` in issues export).

---

## High-priority technical issues

### Broken URLs (404)

**Finding:** **Four** crawled HTML URLs return **404**.

**Evidence (`internal_all.csv` / `response_codes_all.csv`):**

- `http://hogeyecameras.com/resources` (mixed host / HTTP — also a candidate for **HTTPS + host** consolidation)  
- `https://hogeyecameras.com/sim-card-performance-for-ranch-cameras-lte-vs-multi-carrier/`  
- `https://hogeyecameras.com/trap-camera/`  
- `https://hogeyecameras.com/reolink-trap-mods-vs-hogeye-2026/`  

**Why it matters:** Wasted crawl budget, dead ends for users, and lost equity from any internal or inbound links to these paths.

**Recommendation:** Restore content with **301** to the best live URL, fix internal links to the final URLs, or return **410** only if removal is permanent and intentional. Fix **`http://`** and **non-www** variants to the canonical **https://www** or **https** apex policy.

**Priority:** High  

---

### Mixed content and HTTP references

**Finding:** **`issues_overview_report.csv`** reports **Security: Mixed Content** on **19** URLs (**15.08%** of internal URLs in crawl) and **Security: HTTP URLs** on **19** URLs (**15.08%**). Both are flagged **High** priority in the export.

**Why it matters:** Browsers may block or downgrade mixed assets; HTTP links weaken HTTPS guarantees and can affect trust and rendering.

**Recommendation:** Update **all** asset and internal links to **https://** absolute URLs; eliminate **protocol-relative** links (**Security: Protocol-Relative Resource Links** — **5** URLs, Warning). Re-crawl after template/plugin updates.

**Priority:** High  

---

### Client errors (4xx) summary

**Finding:** **Response Codes: Internal Client Error (4xx)** — **4** URLs (**2.67%** of internal URLs), Issue priority **High** (`issues_overview_report.csv`). Aligns with the **404** HTML URLs above.

**Priority:** High (same remediation as broken URLs)  

---

## On-page & structure

### Meta descriptions missing on category hubs

**Finding:** Among **19** indexable **200** HTML URLs, **3** have empty `Meta Description 1` (`internal_all.csv`):

- `https://hogeyecameras.com/category/feral-hog-monitoring/`  
- `https://hogeyecameras.com/category/cellular-security-cameras/`  
- `https://hogeyecameras.com/category/camera-guides/off-grid-cameras/`  

**Why it matters:** Category pages are natural SEO hubs; missing metas forfeit control over snippets for informational and commercial queries.

**Recommendation:** Unique meta descriptions aligned to each category’s scope and Buy Now path.

**Priority:** High  

---

### Short titles

**Finding:** **Page Titles: Below 30 Characters** — **4** URLs (**21.05%** of HTML URLs) (`issues_overview_report.csv`). Examples include very short utility titles on **Buy Now** and **Privacy** paths per `page_titles_all.csv` / `internal_all.csv`.

**Recommendation:** Expand titles where space allows with primary modifiers (hog trap, cellular, ranch) without stuffing.

**Priority:** Medium  

---

### H1 signals (Screaming Frog inconsistency)

**Finding:** **`h1_all.csv`** lists **`Occurrences` = 0** for **12** URLs including homepage, **Buy Now**, **Blog**, and **category** hubs. **`issues_overview_report.csv`** also lists **H1: Missing** — **12** URLs (**63.16%** of HTML). Separately, **H1: Duplicate** affects **7** URLs (**36.84%**).

**Contrast:** `internal_all.csv` lists non-empty **`H1-1`** text for the **homepage** row — so the live DOM may use headings Screaming Frog’s H1 tab did not count the same way (e.g. builder markup).

**Recommendation:** In browser, ensure **one clear `<h1>`** per template (homepage, Buy Now, blog index, categories); resolve duplicate H1s per **H1: Duplicate** rows. Re-crawl after Beaver Builder / theme updates.

**Priority:** Medium–High (validate in DOM; not purely cosmetic if H1 is missing for real users)

---

### Thin content flags

**Finding:** **Content: Low Content Pages** — **8** URLs (**33.33%** of HTML) below default word-count threshold (`issues_overview_report.csv`). Includes **Privacy** (12 words), **Buy Now** (22 words), **camera-login** (37 words), and three **category** pages (~84–85 words).

**Why it matters:** Thin templates can underperform for informational queries and look sparse in quality reviews.

**Recommendation:** Add concise, useful copy on conversion pages (still CTA-forward) and substantive intro copy on category hubs listing article scope.

**Priority:** Medium  

---

### Internal links without anchor text

**Finding:** **Links: Internal Outlinks With No Anchor Text** — **19** URLs (**100%** of URLs in that issue group in this crawl) (`issues_overview_report.csv`).

**Recommendation:** Audit icon-only or wrapped-image links; add descriptive anchor text where it helps users and topical relevance.

**Priority:** Low–Medium  

---

## Performance & media

**Finding:** **`issues_overview_report.csv`** includes sitewide PageSpeed-style flags: e.g. **PageSpeed: Network Dependency Tree** — **29** URLs (**100%** of HTML in that filter); **Improve Image Delivery** — **19** URLs (**100%**); **Images: Over 100 KB** — **24** image references (**63.16%** of image rows in overview).

**Recommendation:** Prioritize **homepage**, **Buy Now**, and top product URLs from GA (`outputs/search-opportunities.md`); compress hero and product imagery; reduce unused CSS per export hints.

**Priority:** Medium  

---

## Assumptions and unknowns

- **Structured data:** Use `structured_data_all.csv` / error reports for a future pass if rich results are in scope; not fully expanded in this document.  
- **Staging** (`staging.hogeyecameras.com`) not crawled here — production-only.  
- **GSC** unavailable — cannot rank fixes by impressions or query.  

---

## Suggested next steps (data)

1. Add **Google Search Console** exports when access exists (`Pages`, `Queries`) to `inputs/gsc/`.  
2. After fixes, re-run Screaming Frog and compare `issues_overview_report.csv` to this baseline.  
