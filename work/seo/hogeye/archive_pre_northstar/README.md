# Archive: Pre-NorthStar Baselines

This folder is archival only. Keep it for rollback and historical reference.

## What is in here

- `live_draft_backups/`
  - Timestamped JSON snapshots pulled from live WordPress draft posts before rewrite steps.
  - Includes multiple checkpoints for some posts as rewrites were refined.

- `git_snapshot_457fd1c/`
  - Local copy of key Hogeye planning/config docs from commit `457fd1c` (pre-NorthStar baseline).

## How to use this archive

- Use when you need to recover old wording or compare before/after.
- Do not use these files as active generation inputs.
- Do not edit these files during normal production work.

## Current working sources (for future work)

Use these paths instead:

- `work/seo/hogeye/` (active strategy docs)
- `work/seo/hogeye/rewrites/` (active rewrite payloads)
- live WP drafts via REST (source of publish-ready content)

## Notes

- This archive exists to keep rollback safe while avoiding drift in active workflows.
- If new archive snapshots are added later, keep them inside `live_draft_backups/` only.

