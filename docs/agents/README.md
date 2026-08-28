# AI agent personas (Cursor / Claude)

These files define **roles** for assistants working in this repo. They are not runtime code—only instructions.

| File | Role |
|------|------|
| [`../../workspace/brand_truth/BRAND_BASELINE.md`](../../workspace/brand_truth/BRAND_BASELINE.md) | **Read first** — brand truth, verified facts, vocabulary, workflows |
| [`AGENT_LIBRARIAN.md`](AGENT_LIBRARIAN.md) | Content memory: registry, voice, ingest, internal links; reads Humanizer + SEO Monitor docs |
| [`AGENT_SEO_MONITOR.md`](AGENT_SEO_MONITOR.md) | Strategy gate + competitive / measurement context (Gate includes **no em dashes** + **concrete field language** per Humanizer / style guide) |
| [`AGENT_CHIEF_EDITOR.md`](AGENT_CHIEF_EDITOR.md) | Final editorial verdict before Google Doc / client review |
| [`../../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md`](../../workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md) | Canonical **humanizer** pass: fact-locked voice, **no em dashes**, **concrete field language**, normal punctuation |
| [`../../workspace/HOGEYE_CONTENT_STYLE_GUIDE.md`](../../workspace/HOGEYE_CONTENT_STYLE_GUIDE.md) | Vocabulary, structure, **concrete field language** tables |

**Monthly shipping:** follow [`.cursor/skills/he-monthly-cycle/SKILL.md`](../../.cursor/skills/he-monthly-cycle/SKILL.md) and [`../MONTHLY_PUBLISHING_WORKFLOW.md`](../MONTHLY_PUBLISHING_WORKFLOW.md) before persona docs.

**Suggested invocation:** paste the “How to invoke…” block from the relevant file at the start of a chat session.

Related: [`../starter.md`](../starter.md) (full repo context for operators and agents).
