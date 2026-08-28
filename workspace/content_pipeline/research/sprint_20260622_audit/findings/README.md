# Client outputs

**Client:** *(template — set from `client_config.yaml` per engagement)*  
**Document:** Outputs folder README (template)  
**Created:** 2026-04-08  

Store **final deliverables** and client-ready drafts here (for example `final-audit.md`, `technical-findings.md`, `keyword-opportunities.md`).

Outputs should reference evidence from `working/` and inputs; do not mix confirmed findings with unresolved assumptions.

---

## Required document header (all `.md` deliverables)

Place this block **immediately after the main `# Title`** in every new or updated output file:

```markdown
**Client:** [Display name] (`[slug]`)  
**Document:** [Short document type — e.g. Final SEO & LLM audit, Technical SEO & structural findings]  
**Created:** YYYY-MM-DD  
```

- **`Client`:** Use `display_name` and `slug` from `client_config.yaml`.
- **`Document`:** A stable, human-readable label so files are identifiable when shared outside the repo.
- **`Created`:** The date this version of the document was **authored or last materially updated** (ISO `YYYY-MM-DD`).

The same pattern applies to **`working/`** notes; use the `(working)` suffix in **Document** where helpful (e.g. `Client facts (working)`).
