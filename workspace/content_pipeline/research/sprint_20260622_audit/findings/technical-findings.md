# Technical SEO & structural findings — HogEye Cameras

## How to read this document

- **Scope:** Production site **`https://hogeyecameras.com/`** — technical and on-page signals from a Screaming Frog bulk export only (no Google Search Console or GA metrics in this file). Staging is out of scope.
- **Evidence:** All counts and URLs come from exports under `clients/hogeye/inputs/screaming_frog/2026.06.22.agt-cursor/` (`crawl_overview.csv`, `internal_all.ndjson`, `issues_overview_report.csv`, and element exports cited below).
- **Crawl window:** Spider **start** 2026-06-22 15:31:05; crawl **elapsed** ~00:00:23; **report** timestamp 2026-06-22 15:31:48 (`crawl_overview.csv`). Per-URL `Crawl Timestamp` in `internal_all.ndjson` is 2026-06-22.
- **Percentages** below use Screaming Frog denominators as reported in `crawl_overview.csv` (e.g. **34** indexable HTML 2xx pages for title/meta/H1 checks; **167** internal URLs for security rows).
- **Baseline comparison:** April 2026 crawl (`2026.04.09.05.15.26`) had **126** internal URLs and **19** indexable HTML 200 pages. This crawl found **167** internal URLs and **34** indexable HTML 200 pages — the site has materially expanded (new blog posts and category hubs).

## Crawl snapshot

| Metric | Value | Notes / source |
| ------ | ----- | ---------------- |
| Total URLs crawled | **197** | `crawl_overview.csv` |
| Total internal URLs | **167** | `crawl_overview.csv` — was **126** in April 2026 |
| Total HTML URLs | **40** | `crawl_overview.csv` — was **23** in April 2026 |
| Indexable HTML URLs (200 OK) | **34** | `internal_all.ndjson` — was **19** in April 2026 |
| Non-indexable HTML URLs | **6** | All **404 Not Found** (`internal_all.ndjson`; `Indexability Status` = Client Error) |
| Internal URLs — **2xx** success | **161** | `crawl_overview.csv` — all content types |
| Internal URLs — **3xx** redirect | **0** | `crawl_overview.csv` |
| Internal URLs — **4xx** client error | **6** | `crawl_overview.csv` (3.05% of 197 crawled URLs) |
| Internal URLs — **5xx** server error | **0** | `crawl_overview.csv` |
| Internal redirect chains / loops | **0** | `crawl_overview.csv` |
| Blocked by robots.txt | **0** | `crawl_overview.csv` |

**HTML response mix:** **34** HTML URLs return **200**, **6** return **404** (`internal_all.ndjson`).

---

## High-priority technical issues

### Broken URLs (404)

| Field | Detail |
| ----- | ------ |
| **Finding** | **6** internal **HTML** URLs return **404 Not Found** — **2** are new vs the April 2026 crawl. |
| **Evidence** | `internal_all.ndjson` / `response_codes_all.ndjson`; `issues_overview_report.csv` — “Response Codes: Internal Client Error (4xx)” — **6** URLs (**3.05%** of 197 crawled URLs), priority **High**. |
| **Why it matters** | Dead ends for users and bots; internal links from high-value trap-monitoring posts point to broken URLs, wasting crawl budget and harming trust on a product site. |
| **Recommended action** | Restore content with **301** to the closest live page, update all internal links to the final URL, or return **410** only if removal is permanent. Fix **`http://hogeyecameras.com/resources`** to the preferred **HTTPS** host. |
| **Priority** | High |

**Example URLs:**

| URL | Status | Delta vs April |
| --- | ------ | -------------- |
| `http://hogeyecameras.com/resources` | 404 (HTTP, non-www) | Unchanged |
| `https://hogeyecameras.com/trap-camera/` | 404 | Unchanged — **10+** inlinks from recent posts (`all_inlinks.ndjson`) |
| `https://hogeyecameras.com/sim-card-performance-for-ranch-cameras-lte-vs-multi-carrier/` | 404 | Unchanged |
| `https://hogeyecameras.com/reolink-trap-mods-vs-hogeye-2026/` | 404 | Unchanged |
| `https://hogeyecameras.com/common-hog-trap-mistakes/` | 404 | **New** — linked from `/corral-hog-trap-hog-trap-comparison-corral-box-drop-net/` |
| `https://hogeyecameras.com/hog-trap-baiting-guide/` | 404 | **New** — linked from `/hog-trapping-techniques-common-hog-trap-mistakes/` (live slug appears to be `/wild-hog-bait-hog-trap-baiting-guide/`) |

---

### Mixed content and HTTP asset URLs

| Field | Detail |
| ----- | ------ |
| **Finding** | **Security: Mixed Content** — **34** HTML pages (**20.36%** of internal URLs); **Security: HTTP URLs** — **19** URLs (**11.38%**). **Protocol-relative resource links** — **5** URLs (**2.99%**), priority **Warning** (`issues_overview_report.csv`). |
| **Evidence** | `security_all.ndjson` — **19** internal URLs use `http://hogeyecameras.com/wp-content/uploads/...` (images and PDFs). All **5** internal PDFs are served over **HTTP** with **no canonical** (`canonicals_all.ndjson`). |
| **Why it matters** | Browsers may block or downgrade mixed HTTP resources on HTTPS pages; warranty PDFs and product images over HTTP weaken trust on a ranch-monitoring product site. |
| **Recommended action** | Replace **http://** with **https://** for all internal assets in media library, theme, and content; remove **protocol-relative** URLs where flagged. Re-crawl after deployment. |
| **Priority** | High |

---

### Redirect chains / loops (internal)

| Field | Detail |
| ----- | ------ |
| **Finding** | **Internal redirect chains:** **0**; **internal redirect loops:** **0** (`crawl_overview.csv`). |
| **Evidence** | `crawl_overview.csv` — “Internal Redirect Chain” and “Internal Redirect Loop” both **0**. |
| **Recommended action** | None required for internal chains based on this crawl. |
| **Priority** | — |

---

### Canonical tag coverage (HTML vs PDF)

| Field | Detail |
| ----- | ------ |
| **Finding** | **All 34** internal HTML URLs returning **200** include a **canonical link element** (self-referencing). **5** internal **PDF** URLs (HTTP) have **no** canonical (`issues_overview_report.csv` — “Canonicals: Missing” — **5** / **39** HTML+PDF 2xx, **12.82%**). |
| **Evidence** | `canonicals_all.ndjson`; `crawl_overview.csv` — canonical **Missing** **5** on PDF assets only. |
| **Why it matters** | HTML canonicals are solid; PDFs without canonicals and served over HTTP are a lower-priority but fixable consistency gap. |
| **Recommended action** | Serve PDFs over **HTTPS**; optional canonical or **noindex** if duplicate PDF URLs appear in future crawls. |
| **Priority** | Low (PDF assets; HTML is covered) |

---

### Robots / noindex on important pages

| Field | Detail |
| ----- | ------ |
| **Finding** | **No** `noindex` or `nofollow` values in `directives_all.ndjson` for crawled HTML. **Blocked by robots.txt:** **0** (`crawl_overview.csv`). |
| **Evidence** | `directives_all.ndjson`; `crawl_overview.csv`. |
| **Recommended action** | None from this crawl; confirm production `robots.txt` and XML sitemap URL(s) in live environment (not confirmed in exports). |
| **Priority** | — |

---

### Indexable duplicates (content)

| Field | Detail |
| ----- | ------ |
| **Finding** | **Exact duplicates:** **0**; **near duplicates:** **0** among internal HTML with 2xx (`crawl_overview.csv` — Content section). |
| **Recommended action** | None indicated by duplicate-content flags in this export. |
| **Priority** | — |

---

## On-page & structure

**Baseline (internal HTML with 2xx — 34 URLs):** Screaming Frog `crawl_overview.csv` summary rows.

| Check | Count | % of 34 HTML (2xx) |
| ----- | ----- | ------------------- |
| **Page titles — missing** | 0 | 0% |
| **Page titles — duplicate** | 2 URLs (1 title string) | **5.88%** — “Blog - HogEye Cameras” on `/blog/` and `/category/blog/` |
| **Page titles — below 30 characters** | 5 | **14.71%** |
| **Page titles — over 60 characters** | 4 | 11.76% |
| **Page titles — over 561 pixels** | 7 | 20.59% |
| **Page titles — same as H1** | 9 | 26.47% |
| **Meta descriptions — missing** | 8 | **23.53%** — all **8** category hub URLs |
| **Meta descriptions — duplicate** | 0 | 0% |
| **Meta descriptions — over 155 characters** | 6 | 17.65% |
| **H1 — missing** | 17 | **50.00%** |
| **H1 — duplicate** | 17 URLs | 50.00% |
| **H1 — multiple** | 17 | 50.00% |
| **H1 — non-sequential** | 2 | 5.88% |
| **H2 — missing** | 5 | 14.71% |
| **H2 — duplicate** | 9 | 26.47% |
| **H2 — multiple** | 21 | 61.76% |
| **Low content pages** (below default word-count threshold) | 4 | **10.26%** of **39** content rows (HTML + PDF context in SF) |

**Thin / low word count (HTML):** `content_all.ndjson` / `internal_all.ndjson` — **buy-now** (22 words), **buy-now-legacy** (15), **camera-login** (37), **privacy-policy** (12 words per `internal_all.ndjson`).

**Orphan URLs:** **0** indexable HTML pages with **0** inlinks (`internal_all.ndjson`).

**Click depth (homepage as start URL):** depth **0:** 1 page; **1:** 10 pages; **2:** 6 pages; **3:** 13 pages; **4:** 4 pages (`internal_all.ndjson`).

**Internal linking:** `issues_overview_report.csv` — **“Internal Outlinks With No Anchor Text”** on **34** / **34** HTML pages (**100%**). Systematic pattern (icon-only or image links without alt text).

**Other:** **URL: Non ASCII Characters** — **2** internal URLs (**1.20%**). **Images: Missing Alt Text** — **4** (**6.45%** of images). **Images: Over 100 KB** — **40** (**64.52%** of images). **Images: Missing Size Attributes** — **18** (**29.03%**).

**April delta:** H1 missing dropped from **63%** (12/19) to **50%** (17/34) by proportion, but **17 absolute URLs** still lack an H1 in SF’s parse — including homepage and Buy Now. Meta missing expanded from **3** to **8** URLs as **8 category hubs** entered the crawl.

---

## Category / hub page observations

Evidence: `internal_all.ndjson` (status, indexability, title, meta, canonical, word count, crawl depth, inlinks).

| URL | Status | Indexability | Title | Meta | H1 (SF) | Canonical | Depth | Inlinks | Words |
| --- | :---: | :---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `/` | 200 | Indexable | Hogeye Camera Systems: Smarter Hog Trapping… (58) | Present | **Missing** | Self | 0 | 77 | 643 |
| `/blog/` | 200 | Indexable | Blog - HogEye Cameras (21) | Present (placeholder text — see below) | **Missing** | Self | 1 | 48 | 255 |
| `/buy-now/` | 200 | Indexable | Buy Now - HogEye Cameras (24) | Present | **Missing** | Self | 1 | 71 | 22 |
| `/camera-resources/` | 200 | Indexable | Hog Trap Camera Resources \| HogEye Setup Guide | Present | **Missing** | Self | 1 | 100 | 975 |
| `/hog-traps/` | 200 | Indexable | Hog Traps - HogEye Cameras | Present | **Missing** | Self | 1 | 51 | 354 |
| `/category/feral-hog-monitoring/` | 200 | Indexable | Feral Hog Monitoring - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 362 |
| `/category/cellular-security-cameras/` | 200 | Indexable | Cellular Security Cameras - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 362 |
| `/category/camera-guides/` | 200 | Indexable | Camera Guides - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 361 |
| `/category/camera-guides/off-grid-cameras/` | 200 | Indexable | Off-Grid Cameras - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 361 |
| `/category/feral-hog-management/` | 200 | Indexable | Feral Hog Management - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 362 |
| `/category/feral-hog-educational-awareness/` | 200 | Indexable | Feral Hog Educational & Awareness - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 364 |
| `/category/blog/` | 200 | Indexable | Blog - HogEye Cameras (duplicate title) | **Missing** | **Missing** | Self | 3 | 24 | 360 |
| `/category/uncategorized/` | 200 | Indexable | Uncategorized - HogEye Cameras | **Missing** | **Missing** | Self | 3 | 24 | 360 |

**Structural note:** Category hubs now carry **~360 words** (up from **~84–85** in April) but still lack **meta descriptions** and **H1** in SF’s parse. SF may be seeing Beaver Builder section headings as **H2** only — confirm in DOM whether H1 is absent or rendered in a non-standard element.

---

## Buy Now / conversion page observations

**URL:** `https://hogeyecameras.com/buy-now/` (`internal_all.ndjson`)

| Signal | Value |
| ------ | ----- |
| Status | **200** |
| Indexability | **Indexable** |
| Title | **Buy Now - HogEye Cameras** — **24** characters (`issues_overview_report.csv` — below 30 chars) |
| Meta description | Present — begins “Shop HogEye Shop Legacy Camera Parts Here…” (repeated phrasing — verify in CMS) |
| H1 | **Missing** per `h1_all.ndjson` |
| H2 | Present (e.g. “Shop Legacy Camera Parts Here” pattern in `internal_all.ndjson`) |
| Canonical | `https://hogeyecameras.com/buy-now/` (self) |
| Word count | **22** — below SF low-content threshold |
| Crawl depth | **1** |
| Inlinks | **71** — highest internal visibility alongside `/camera-resources/` |

**Compared to informational posts:** Article URLs (e.g. `/net-camera-trap-remote-hog-trapping/`) have **hundreds–thousands** of words and visible H1 in `h1_all.ndjson`. **Buy Now** is structurally thin and lacks an H1 in SF’s parse — high priority for template fixes on the primary conversion URL.

**Related:** `https://hogeyecameras.com/buy-now-legacy/` — **15** words, **H1** missing, **14** inlinks.

---

## URL-level examples table

| URL | Issue type | Severity | Recommended fix |
| --- | --- | --- | --- |
| `https://hogeyecameras.com/trap-camera/` | 404; linked from 10+ posts | High | 301 to `/steel-camera/` or restore; update all inlinks |
| `https://hogeyecameras.com/common-hog-trap-mistakes/` | 404 (new) | High | 301 to `/hog-trapping-techniques-common-hog-trap-mistakes/` or restore |
| `https://hogeyecameras.com/hog-trap-baiting-guide/` | 404 (new) | High | 301 to `/wild-hog-bait-hog-trap-baiting-guide/` |
| `http://hogeyecameras.com/resources` | 404; HTTP / host | High | Redirect to live HTTPS resource hub; fix PDF link in user manual |
| `https://hogeyecameras.com/sim-card-performance-for-ranch-cameras-lte-vs-multi-carrier/` | 404 | High | Restore or 301 to related connectivity post |
| `https://hogeyecameras.com/reolink-trap-mods-vs-hogeye-2026/` | 404 | High | Restore or 301 to comparison content |
| `https://hogeyecameras.com/` | Mixed content; no H1 (SF) | High | HTTPS assets; add single primary H1 in theme |
| `https://hogeyecameras.com/buy-now/` | No H1; 22 words; short title; mixed content | High | Add H1 + product copy; extend title; fix HTTP assets |
| `https://hogeyecameras.com/category/feral-hog-monitoring/` | Missing meta; no H1 (SF); mixed content | High | Unique meta; confirm H1 in category template |
| `https://hogeyecameras.com/category/cellular-security-cameras/` | Same category-hub pattern | High | Same |
| `https://hogeyecameras.com/category/camera-guides/` | Same | High | Same |
| `https://hogeyecameras.com/blog/` | Missing H1; placeholder meta (Lorem/Texas home design text) | Medium | Replace meta; fix heading hierarchy |
| `https://hogeyecameras.com/category/blog/` | Duplicate title with `/blog/`; missing meta | Medium | Differentiate title; add meta |
| `https://hogeyecameras.com/camera-resources/` | HTTP PDF links; mixed content | Medium | HTTPS PDF URLs |
| `https://hogeyecameras.com/privacy-policy/` | 12 words in SF count | Medium | Verify full legal text in crawlable DOM |
| `https://hogeyecameras.com/hog-trapping-cameras-compared-2026-hogeye-vs-trail/` | Duplicate H1 (×2); links to 2 broken URLs | Medium | Single H1; fix outbound internal links |
| `http://hogeyecameras.com/wp-content/uploads/...` (PDFs) | HTTP; missing canonical | Low | HTTPS + optional canonical strategy |

---

## Priority action list

### Sprint 1 — Immediate technical fixes

- Resolve **6** **404** HTML URLs — prioritize **`/trap-camera/`** (most inlinks) and **2 new** slug mismatches (`common-hog-trap-mistakes`, `hog-trap-baiting-guide`).
- Fix **`http://hogeyecameras.com/resources`** and enforce **HTTPS** host consistency.
- Eliminate **mixed content** on **34** HTML pages and **HTTP** internal URLs (**19** assets per `security_all.ndjson`).

### Sprint 2 — Structural / on-page fixes

- Add **one clear H1** per template on **17** URLs where SF reports **missing H1** — especially **homepage**, **Buy Now**, **category hubs**, **blog index**.
- Write **unique meta descriptions** for **8** category hubs (`meta_description_all.ndjson`).
- **Buy Now** and **legacy Buy Now:** increase body copy (**22** / **15** words); extend title beyond 30 characters.
- Resolve **duplicate / multiple H1** on **17** article URLs — many show identical duplicated H1 text (template block repeating title as H1 twice per `h1_all.ndjson`).
- Differentiate **duplicate title** “Blog - HogEye Cameras” on `/blog/` vs `/category/blog/`.
- Improve **internal anchor text** — **100%** of HTML pages have outlinks without anchor text (`issues_overview_report.csv`).

### Sprint 3 — Enhancement / cleanup

- Shorten **overlong meta descriptions** (**6** pages > 155 chars) and **titles** over pixel limits (**7** pages).
- **H2** missing on **5** pages; **duplicate H2** on **9** pages.
- **Image** weight and **alt** — **64.52%** of images over **100 KB**; **4** missing alt text.
- **Security headers** (HSTS, CSP, X-Frame-Options) — flagged on most URLs; treat as infrastructure backlog with hosting/dev team.

---

## Notable examples

- **`/trap-camera/`** — Persistent **404** since April crawl; now linked from **10+** recent trap-workflow posts (`all_inlinks.ndjson`) — highest-impact broken internal link.
- **`/common-hog-trap-mistakes/`** and **`/hog-trap-baiting-guide/`** — **New 404s** since April; likely slug changes without redirects (live content exists at different URLs).
- **`https://hogeyecameras.com/buy-now/`** — Primary conversion path with **22** words, **no H1** in SF, **71** inlinks — strong internal visibility, weak on-page depth.
- **Eight category hubs** under `/category/` — all **missing meta descriptions** and **H1** in SF; word counts improved to **~360** vs **~85** in April but SEO templates still need meta/H1 pass.
- **`https://hogeyecameras.com/blog/`** — Meta description contains **Lorem ipsum** and **Texas home design** text (`internal_all.ndjson`) — placeholder still in CMS.
- **Article template** — **17** URLs show **duplicate identical H1** pairs (title repeated twice as H1-1 and H1-2) — systematic Beaver Builder or AIOSEO pattern.
- **`http://hogeyecameras.com/wp-content/uploads/...` PDFs** — **5** warranty/manual PDFs over **HTTP**, linked from **camera-resources**; no canonicals.
- **Sitewide:** **Every** crawled HTML page (**34** / **34**) has at least one **internal outlink without anchor text**.
- **Site growth:** Internal URL count **+33%** and indexable HTML **+79%** vs April — content sprint is working; technical debt (404s, H1/meta templates) scales with new posts unless fixed at template level.
