# Hogeye - Safe Staged Workflow (Draft-First)

**Principle:** nothing touches WordPress until you approve it, **one piece at a time**.

---

## Stage 1: Generate locally (safe)

Goal: produce local draft bundles + review packets only.

**Outputs (recommended):**
- `bundle.json` (single source of truth)
- `article.html` (easy review)
- `meta.txt` (meta title + description + keyword)
- `checklist.md` (validation + human review prompts)

**Checkpoint:** human spot-check the content quality before any WP calls.

---

## Stage 2: Updates require diffs + backups (safe)

Before updating any existing post/page:
- Fetch the current WP content
- Save a backup JSON locally
- Produce a before/after diff report

**Checkpoint:** human approves the diff.

---

## Stage 3: Dry-run (safe)

Simulate the API calls we would send:
- endpoint + payload
- create vs update
- risk flags

**Checkpoint:** payloads match intent (especially updates).

---

## Stage 4: Publish ONE piece as draft (writes to WP)

For each piece:
- show summary (title, slug, word count, links)
- confirm\n+- publish as **draft**
- record the result in an audit log (time, WP ID, URL)

**Checkpoint:** review the WordPress draft in the editor.

---

## Rollback posture (updates only)

If an update draft is wrong:
- rollback from the saved backup (restore previous JSON payload)
- re-run after fixing the local draft

