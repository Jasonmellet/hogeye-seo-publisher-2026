# Agent guidance

<!-- agent-ops -->
## Deployment

Follow `.agent-ops/DEPLOYMENT_POLICY.md`: branch → pull request → required CI → merge to `main` → deploy from `main`. Never run production deploy commands from an agent shell.

## Thread notes

Record durable thread context in `docs/threads/YYYY-MM-DD-short-slug.md` using `docs/threads/_template.md`. Update Confluence only when the `thread-archive` skill classifies a thread as needing it, and only after confirmation.
