# Research archive (HogEye content pipeline)

Dated research bundles support monthly queue creation, briefs, and research packs.

## Active bundle (June 2026 audit sprint)

**[`sprint_20260622_audit/`](sprint_20260622_audit/INDEX.md)** — full migration from Advanced SEO Analysis:

- Screaming Frog (Jun 2026), GSC, GA4, DataForSEO ($7.08 / 320 SERP / 45 LLM / 28 ChatGPT)
- Synthesis docs + WD stakeholder context
- **Start here** for July 2026+ planning

## Older bundles (still valid for voice/history)

| Folder | Role |
| ------ | ---- |
| `2026-03-keyword-universe/` | March keyword shortlists |
| `2026-03-transcript-dfs/` | Transcript-backed keyword candidates |
| `2026-04-five-piece-blueprint.md` | April trap-release series plan |
| `trap_release_20260318_210051Z/` | Trap release DataForSEO + GSC maps |

## Convention for new imports

When Advanced SEO Analysis completes a new phase:

```
workspace/content_pipeline/research/sprint_YYYYMMDD_<label>/
  INDEX.md
  inputs.json
  findings/
  working/
  inputs/
```

Copy SF exports to `work/seo/screaming_frog/<crawl-id>/` and log in `workspace/technical_seo/CRAWL_COMPARISON.md`.
