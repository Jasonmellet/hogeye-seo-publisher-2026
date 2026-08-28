# Edit collaboration — `may26_05` (piece 5 of 5)

**Title:** Corral Trap vs. Box Trap vs. Drop Net: Which Hog Trap Is Right for Your Property?  
**Phase:** Minor Google suggestions **accepted**; **larger structural / copy edits** tracked here with Jason ↔ Cursor (then Librarian for ship checklist).

---

## Canonical locations

| What                               | Where                                                                                |
| ---------------------------------- | ------------------------------------------------------------------------------------ |
| Google Doc (tab **5: Corral…**)    | https://docs.google.com/document/d/1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y/edit |
| Plain export (after each Doc save) | `workspace/content_pipeline/monthly/2026-05/drafts/_google_sync/may26_05_plain.txt`  |
| Markdown draft                     | `workspace/content_pipeline/monthly/2026-05/drafts/may26_05_draft.md`                |

**Refresh export** (from repo root):

```bash
npm run google:export-tab-plain -- --tab "Corral Trap vs. Box Trap" --out workspace/content_pipeline/monthly/2026-05/drafts/_google_sync/may26_05_plain.txt
```

**Refresh archives** (comments + suggestions + `REVIEW_BUNDLE_LATEST.md`):

```bash
npm run google:archive-doc-review
```

For **resolved** threads and non–may26-scoped comments, use: `npm run google:render-review-bundle-full`.

---

## How to use this doc

1. **Jason:** Add each big edit as a **numbered** item (section heading in Google, paste of paragraph, or “see comment @ …”).  
2. **Cursor:** Implement in `may26_05_draft.md`, check internal links / claims, tick **Done** and add a one-line note.  
3. **When the tab matches the draft:** run the export again, skim diff, then regen `content/posts/may26_05_wp_draft.json` and move pipeline to `client_approved` / `wp_json` as appropriate.

---

## Big edits (add below)

### 1. Schell comment `AAAB3xdvWyg` — trap category order (price ladder)

- **Doc anchor / section:** “The Three Main Wild Hog Trap Categories”  
- **Desired change:** Present categories as **box → net → corral** (less expensive → more expensive); match body section order, comparison table columns, and monitoring paragraph order.  
- **Done:** [x] — applied in `may26_05_draft.md` (intro bullets + summary sentence + H2 order + table + monitoring + FAQ “most effective” order); intro note clarifies “typical commercial” because DIY corral can sit between box and net on spend.

### 2. Schell comment `AAAB3xdvWzs` — corral definition + DIY / BPT context

- **Doc anchor / section:** First sentence under “How Corral Traps Work” (quoted in Drive).  
- **Desired change:** “Match from above” across intro corral bullet + body + FAQ; add concise **DIY vs. livestock panels vs. commercial panel kit** note and **Big Pig Traps** six-panel / two-gate, **larger circumference** for **larger sounders** (per Schell background).  
- **Done:** [x] — intro bullet and FAQ aligned to circular/oval + panel types; new bridge paragraph after gate sentence; “What is a corral trap?” and commercial pricing line tightened to match.

### 3. Schell comment `AAAB3xdvW44` — BPT Panel Trap circumference / capacity

- **Doc anchor / section:** “Commercial systems: Big Pig Traps…”  
- **Desired change:** Panel Trap **~25 ft circumference**; can **comfortably hold 40+ hogs** (per Schell).  
- **Done:** [x] — **Commercial systems** paragraph updated with **~25 ft** circumference and **40+** hog capacity for the stock six-panel / two-gate Panel Trap; earlier BPT sentence in “How Corral Traps Work” kept qualitative to avoid duplicating specs.

### 4. Schell comment `AAAB3xdvW60` — net trap positioning (open vs forest, capacity, cost-effective)

- **Doc anchor / section:** H2 “Best for Large Sounders in Open Areas” (suspended net).  
- **Desired change:** Nets **best for smaller sounders in open areas**; **tree set** when hogs are in **forest**; typical **20–30 hogs** easily; nets as **effective, cost-effective** for **larger-sounder capture**.  
- **Done:** [x] — H2 + net section (geography paragraph, capacity, cost, setup, “best for,” effort line), comparison table net rows, how-to-choose, multi-trap line, FAQ “most effective,” and three-category summary updated.

### 5. Schell comments `AAAB3xdvXBE`, `AAAB3xdvXEk`, `AAAB3xdvXBQ`, `AAAB3xdvXEI` — net cost, tree anchors, solo training/dispatch, affordability & wear

- **`AAAB3xdvXBE`:** Cost line — most users are **individuals**; no typical **paid installation** add-on; **monitoring hardware** not always required but **live video** cuts trips / times the drop.  
- **`AAAB3xdvXEk`:** **Tree-set** nets can anchor to **trees** vs long **T-post** runs—saves time/equipment; place the trap **where hogs already are**.  
- **`AAAB3xdvXBQ`:** Emphasize **training** on flexible systems for **individual** operators; **dispatch/removal** + **disease** awareness for **any** trapper (solo or crew).  
- **`AAAB3xdvXEI`:** Nets as **affordable** for individuals; **20–40** hog yields; **wear/tear** → repairs / replacement nets.

### 6. Schell comments `AAAB3xdvXE4`, `AAAB3xdvXFo` — net “best for” bullet + comparison table

- **`AAAB3xdvXE4`:** Replace “Intensive management programs…” with **individuals / smaller programs** + **cost-effective** hog management **on their land**.  
- **`AAAB3xdvXFo`:** Table **Box → Net → Corral** (already column order); **split corral** into **DIY vs. commercial** columns with distinct **capacity / cost / setup / best sounder** cells.

### 7. Schell comments `AAAB3xdvXFw`, `AAAB3xdvXF8`, `AAAB3xdvXGE` — How to Choose, budget line, multi-trap roles

- **`AAAB3xdvXFw`:** Rework **3–8 / 8–20 / 20+** bullets—**corral (steel)** for **reuse** and **larger** work; **net** **cost-effective** on **open/tree-set**; **20+** favors **commercial steel** first, net secondary with **wear** tradeoff.  
- **`AAAB3xdvXF8`:** Budget example → **~$2,199** net vs **$5,000+** corral for **whole sounder in one night**.  
- **`AAAB3xdvXGE`:** Multi-trap paragraph → **corral** for **larger sounders** + **repeat tapping** (**steel outlasts fabric**); **net** for **smaller whole-sounder** / **~15–25** band + **cost-effective**; **box** stragglers. FAQ “most effective” aligned (later superseded by **`XRU`**).

### 8. Schell comments `AAAB3xdvXGU`, `AAAB3xdvXRU` — monitoring order + FAQ “most effective”

- **`AAAB3xdvXGU`:** Monitoring section ordered **box → net → corral** (already); added explicit intro line tying to article sequence.  
- **`AAAB3xdvXRU`:** FAQ **“What is the most effective hog trap?”** → **box** pairs only; **nets mobile**, singles or **25+** sounders; **corrals** for **larger / longer-term**, **40+** with **circumference**; match **your land**. Disadvantages FAQ net line de-conflicted with solo-operator framing.

---

## Resolved (log)

- **2026-04-22 — `AAAB3xdvWyg`:** Three trap categories reordered to box → net → corral (price ladder); sections and comparison table aligned.
- **2026-04-23 — `AAAB3xdvWzs`:** Corral intro/body/FAQ wording aligned to “How Corral Traps Work” opening; DIY / panel / BPT circumference context added; commercial line references six panels + two gates explicitly.
- **2026-04-23 — `AAAB3xdvW44`:** Big Pig Traps Panel Trap: ~25 ft circumference, 40+ hog capacity in **Commercial systems** paragraph.
- **2026-04-23 — `AAAB3xdvW60`:** Net trap H2 and body refocused (open / smaller–mid sounders, tree sets in forest, ~20–30 typical capacity, cost-effective large-sounder framing); table + choose + FAQ aligned.
- **2026-04-23 — `AAAB3xdvXBE` / `XEk` / `XBQ` / `XEI`:** Net **Capacity and Cost** (individual buyers, no install line item, live video vs dedicated hardware, 20–40 yields, durability); **Setup** (tree anchors vs T-posts, training, dispatch/disease, phone video); closing paragraph + core limitation + table capacity column.
- **2026-04-23 — `AAAB3xdvXE4` / `XFo`:** Net “best for” last bullet → individuals/smaller programs; comparison table → **Corral (DIY)** vs **Corral (commercial)** + intro line on column order.
- **2026-04-23 — `AAAB3xdvXFw` / `XF8` / `XGE`:** How to Choose tiers + budget one-night example + multi-trap paragraph + FAQ corral-vs-net emphasis (steel durability vs net cost / ~15–25 band).
- **2026-04-23 — `AAAB3xdvXGU` / `XRU`:** Monitoring intro (**box → net → corral**); FAQ “most effective” per Schell (mobile nets, **25+**, corral **40+** / circumference); disadvantages net bullet aligned.

---

## Librarian (when this piece locks)

- Regenerate `content/posts/may26_05_wp_draft.json` from final `may26_05_draft.md`.  
- Cross-check `PACKAGE_INDEX.md` / `CONTENT_REGISTRY.md` status and internal links (`/trap-camera/`, steel/net comparison paths per brief).  
- If Schell’s Google-only edits won again: ensure `may26_05_plain.txt` date matches ship commit for audit.
