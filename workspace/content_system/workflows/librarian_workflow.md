# HogEye Librarian Workflow

The librarian workflow keeps shared doctrine docs aligned to new derived notes without silently editing active content artifacts.

## Scope and safety

- Allowed targets: shared doctrine/config/prompt/workflow docs only
- Disallowed targets: active monthly briefs, research packs, drafts, QA files, and handoff files
- Update policy: proposal-first, then selective apply

## Commands

Generate a new proposal from recent derived notes:

```bash
npm run librarian:audit -- --limit 10
```

Apply only approved proposal items:

```bash
npm run librarian:apply -- --proposal /abs/path/to/proposal.json
```

Optional operator override to apply pending items after review:

```bash
npm run librarian:apply -- --proposal /abs/path/to/proposal.json --apply-all-pending
```

## Proposal lifecycle

1. Audit command writes:
   - `workspace/content_system/alignment/proposals/<proposal_id>.json`
   - `workspace/content_system/alignment/proposals/<proposal_id>.md`
2. Reviewer marks items as `approved` or `rejected` in the JSON file.
3. Apply command updates only allowed target files for selected items.
4. Apply command writes logs to:
   - `workspace/content_system/alignment/applied/<proposal_id>.applied.json`
   - `workspace/content_system/alignment/applied/<proposal_id>.applied.md`
