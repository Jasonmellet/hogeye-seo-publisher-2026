# Theo Content System Replication Guide

Purpose: document the current Theo content operating system so it can be replicated for another client without losing discipline, voice controls, or publishing safety.

This guide is based on the live implementation in this repository, including scripts, prompts, rules, workflows, and templates.

## 1) System overview

The system is a human-gated content pipeline with four major loops:

1. Ingestion loop (media -> transcript -> derived notes)
2. Editorial loop (source notes -> brief -> draft -> review -> final)
3. Alignment loop (Theo Injection for artifact upgrades; Theo Librarian for shared doctrine refresh)
4. Distribution loop (final markdown -> WordPress draft only)

Core design principles:

- Repo is source of truth for approved copy and editorial history.
- WordPress is downstream delivery, not authoritative source text.
- Evidence outranks inference.
- Human approval is required before `final/` and before any live publish action.
- Automation defaults to draft status and does not auto-publish.

## 2) Repository architecture and folder semantics

Canonical folders and intent:

- `knowledge/source-notes/`: raw and semi-structured inputs
- `knowledge/source-notes/video-inbox/`: transient local media drop zone (gitignored)
- `knowledge/source-notes/transcriptions/raw/`: Whisper API artifacts (`.verbose.json`, `.txt`)
- `knowledge/source-notes/transcriptions/processed/`: transcript markdown plus metadata
- `knowledge/source-notes/video-derived-notes/`: structured editorial extraction from transcripts
- `briefs/`: commissioning artifacts
- `drafts/`: working manuscripts
- `final/`: approved canonical markdown
- `archive/`: superseded artifacts
- `knowledge/alignment/proposals/`: librarian proposals (pre-approval)
- `knowledge/alignment/applied/`: librarian applied logs (post-approval)
- `prompts/`: reusable workflow and system prompts
- `config/`: governance and validation contracts
- `workflows/`: process definitions and handoffs
- `templates/`: reusable content and review scaffolds
- `scripts/`: automation (transcription, extraction, validation, WordPress sync)

## 3) Runtime and dependencies

Minimum runtime:

- Node.js `>=18` (native `fetch`)
- `tsx`, `typescript`, `dotenv`, `gray-matter`
- `ffmpeg` available on `PATH` for video and oversize media handling

Key npm scripts:

- `npm run transcribe -- <media-path>`
- `npm run transcribe -- --auto <media-path>`
- `npm run process-transcript -- <processed-transcript.md>`
- `npm run validate-frontmatter -- <markdown-path>`
- `npm run wp:create-draft -- <final-file.md>`
- `npm run wp:update-post -- <postId> <final-file.md>`
- `npm run openai:ping`

Environment contract (`.env`):

- `OPENAI_API_KEY`
- `OPENAI_NOTES_MODEL` (optional override; scripts default to **`gpt-5.4-mini`**)
- `WP_SITE_URL`
- `WP_USERNAME`
- `WP_APP_PASSWORD`
- `DEFAULT_AUTHOR` (optional)
- `DEFAULT_CATEGORY` (optional)
- `DEFAULT_STATUS` (optional; still draft-first unless explicitly bypassed)
- `WP_FORCE_DRAFT` (default true behavior)

## 4) Ingestion system internals

### Stage 1: media -> transcript (`scripts/transcribe_video.ts`)

Input:

- One media file path from `video-inbox` (or any file path)

Behavior:

1. Validate input path exists and is a file.
2. Detect whether file is a video container by extension (`.mov`, `.mp4`, `.mkv`, etc.).
3. If file is a video, or if file size exceeds 25 MB, run `ffmpeg` extraction to mono MP3:
   - codec `libmp3lame`
   - 1 channel
   - 16000 Hz
   - 64k bitrate
4. Enforce OpenAI size ceiling (25 MB) on upload artifact.
5. Submit upload to OpenAI Audio Transcriptions API (`whisper-1`, `verbose_json`).
6. Persist outputs:
   - `transcriptions/raw/<timestamp>_<slug>.verbose.json`
   - `transcriptions/raw/<timestamp>_<slug>.txt`
   - `transcriptions/processed/<timestamp>_<slug>.md`
7. Populate processed markdown frontmatter with provenance:
   - `source_media`
   - `source_filename`
   - `extracted_audio` (when extraction occurred)
   - `transcribed_at`
   - `model`, `api`, optional `language`, optional `duration_seconds`
   - `word_count`
   - `raw_json`, `raw_txt`
8. If `--auto` is passed, invoke Stage 2 (`process_transcript.ts`) using `tsx` CLI via `process.execPath`.

Operational effect:

- The pipeline standardizes upload format and avoids manual audio preprocessing.
- It captures enough provenance to audit what was uploaded versus original media.
- It keeps media transient and text artifacts durable.

### Stage 2: transcript -> derived notes (`scripts/process_transcript.ts`)

Input:

- One processed transcript markdown file

Behavior:

1. Parse transcript markdown with `gray-matter`.
2. Build chat request to OpenAI Chat Completions:
   - system prompt embedded in script
   - user prompt generated in script (`buildUserPrompt`)
   - model from `OPENAI_NOTES_MODEL` or fallback default
   - controlled temperature (`NOTES_TEMPERATURE`)
3. Enforce extraction discipline in prompt:
   - not generic summary
   - prioritize strongest distinctive idea
   - preserve sharp distinctions and refusals
   - output required section schema
   - no fabricated facts or unsupported cases
4. Strip code fences from model output if present.
5. Write derived artifact to `video-derived-notes/<timestamp>_<slug>.md` with frontmatter:
   - `source_transcript`
   - `derived_at`
   - `model`
   - `editorial_spec_version`
   - `prompt_system`
   - `title_override` (optional if provided)

Operational effect:

- Converts long-form speech into reusable editorial substrate.
- Moves writing context from raw transcript reading to structured extraction.
- Creates an explicit prompt version marker for regeneration and drift control.

## 5) How ingestion changes writing behavior

Without ingestion:

- Writing model relies on sparse notes, generic abstractions, and prior prompt memory.

With ingestion:

- Writing starts from transcript-grounded derived notes with explicit:
  - core ideas
  - signature language
  - tensions
  - strategic concepts
  - argument patterns
  - content angles
  - caution signals

Result:

- Better thesis quality and argument spine
- Lower risk of fabricated specifics
- Reduced generic consulting language
- More consistent Theo-specific distinctions across assets

## 6) Context injection architecture

Context is injected in layers. This is mostly manual orchestration in Cursor plus deterministic script inputs.

### Layer A: hard constraints (always-on context)

- `config/evidence_and_examples.md`
- `config/content_schema.md`
- `config/frontmatter_standard.md`
- `workflows/approval_policy.md`

These define what is allowed, what is required, and what fails review.

### Layer B: brand and doctrine context

- `knowledge/brand/theo_voice_guide.md`
- `knowledge/brand/messaging_principles.md`
- `knowledge/brand/language_do_not_use.md`
- Relevant `video-derived-notes/*.md`

These shape voice, boundaries, and argument quality.

### Layer C: task-specific workflow context

Examples:

- Outline: `prompts/workflow/create_outline.md` + system prompt
- Drafting: `prompts/workflow/draft_article.md` + system prompt
- Injection: `prompts/workflow/theo_injection.md` or selective variant
- Librarian audit/apply: dedicated librarian prompts

### Layer D: artifact context

- Current brief or draft markdown (full text, including frontmatter)
- Source notes and citations
- Target template headings
- Explicit out-of-scope constraints

### Layer E: operational metadata

- stage by file path (`briefs/`, `drafts/`, `final/`)
- validation result from `validate_frontmatter`
- quality scorecard and final checklist status

Practical packaging rule:

- Use fewer, high-quality source files deeply (especially 1-3 derived notes) instead of many shallow references.

## 7) Writing model behavior contract

Primary writing model behavior is constrained by:

- `prompts/system/theo_writer_system_prompt.md`
- workflow prompt selected for the current step
- evidence hierarchy rules
- explicit source notes and derived notes

Required writing behaviors:

- No invented facts, client details, metrics, dates, or quotes
- Executive, diagnostic tone
- Distinctive framing (not interchangeable consulting prose)
- Clear thesis, tension, consequence
- Honest uncertainty on thin evidence
- Human review before finalization

## 8) Editorial loop (brief -> draft -> final)

Process contract:

1. Intake inputs in `knowledge/source-notes/`.
2. Create accepted brief in `briefs/`.
3. Build outline and draft in `drafts/`.
4. Run revision passes and human edits.
5. Complete:
   - `templates/review/final_review_checklist.md`
   - `templates/review/quality_scorecard.md`
6. Ensure frontmatter passes validation and includes required approval fields.
7. Move approved artifact to `final/`.

Hard gates:

- No automatic failure on scorecard
- `status: approved` for canonical final files
- Named reviewer and approver metadata

## 9) Theo Injection system (artifact-level upgrade loop)

Purpose:

- Upgrade an existing brief or draft so it reflects source-backed Theo thinking.

Modes:

- Full-document injection: `prompts/workflow/theo_injection.md`
- Selective injection for operational docs: `prompts/workflow/theo_injection_selective.md`

Required safeguards:

- Do not invent facts or new case claims
- Do not silently overwrite without versioning discipline
- Preserve stage-required frontmatter keys
- Add provenance fields on injected artifacts:
  - `theo_injection_sources`
  - `theo_injection_at`

When to use:

- Older artifacts predating high-quality derived notes
- Drafts with generic consulting drift
- Briefs missing Theo-grade thesis and tension

When not to use:

- No relevant derived notes
- Need for genuinely new research facts

## 10) Theo Librarian system (shared doctrine refresh loop)

Purpose:

- Keep shared guidance layers aligned with evolving derived notes.

Scope:

- Allowed targets: `knowledge/brand/`, selected `config/`, selected `prompts/`, outreach/email guidance when in scope
- Prohibited auto-updates: `final/`, active `briefs/`/`drafts/`, ingestion scripts, publishing behavior

Workflow:

1. Audit new derived notes against candidate docs.
2. Save proposal in `knowledge/alignment/proposals/`.
3. Human reviewer approves/narrows/rejects item-by-item.
4. Apply only approved items using apply prompt.
5. Record applied log in `knowledge/alignment/applied/`.

Proposal discipline:

- each item must specify source path(s), target file, update type, rationale, confidence, overreach check

Update types:

- `add`, `strengthen`, `reconcile`, `remove`, `no change`

Confidence rubric:

- High, Medium, Low with explicit defer/no-change bias on ambiguity

Cadence:

- per-note light audits
- weekly grouped audits
- monthly full refresh

## 11) Validation and safety controls

### Frontmatter validator (`scripts/validate_frontmatter.ts`)

Stage detection by path:

- `briefs/`, `drafts/`, `final/`, `templates/`, skip others

Checks:

- required keys by stage
- `approval_required` must be boolean true for drafts and final
- final-specific required keys:
  - `reviewer`
  - `approved_by`
  - `approved_at`
  - `cta`
  - `status`
  - `wp_category`
- final `status` must equal `approved`

### Evidence integrity

`config/evidence_and_examples.md` prevents:

- fabricated names, quotes, metrics, outcomes
- implied engagements without clearance
- unattributed authority claims

### Publishing safety

- WordPress scripts are draft-first by design
- `WP_FORCE_DRAFT` default behavior holds status to draft unless explicit override flag is passed
- live publish remains human action in WordPress

## 12) WordPress sync behavior

Scripts:

- `scripts/create_wp_draft.ts`
- `scripts/update_wp_post.ts`
- helper layer `scripts/wp_common.ts`

Field mapping:

- frontmatter `title` -> WP `title`
- frontmatter `slug` -> WP `slug`
- markdown body -> WP `content`
- optional `excerpt` -> WP `excerpt`
- `wp_category` and `wp_tags` resolved to IDs through WP REST lookups

Important:

- scripts warn if file is not in `/final/` (policy expectation)
- scripts still require human operational judgment and team awareness

## 13) Email and derivative constraints

For outbound Theo email copy:

- opening required: `Dear {{first_name}},`
- closing required: `Here Always,` then signature block
- no em dash in email body copy
- one clear ask, short and plain executive language
- no new factual claims beyond approved parent and source notes

Reference: `config/email_format_rules.md`.

## 14) Replication blueprint for a new client

Replicate in this order.

### Step 1: copy system skeleton

Bring over:

- folder structure (knowledge, briefs, drafts, final, archive, config, prompts, workflows, templates, scripts)
- npm scripts and dependencies
- validator and WordPress scripts
- transcription and transcript processing scripts

### Step 2: replace client doctrine layer

Swap Theo-specific brand docs with client-specific equivalents:

- voice guide
- messaging principles
- language anti-patterns
- audience and offers docs

Do not weaken:

- evidence rules
- frontmatter discipline
- approval policy
- draft-first publishing defaults

### Step 3: initialize source capture

- create a media inbox and transcript flow for the new client
- run Stage 1 and Stage 2 on at least 3-5 source recordings
- confirm derived notes are usable for thesis, tensions, and voice markers

### Step 4: re-anchor prompts

Adjust only client references in:

- `prompts/system/*`
- drafting and outline prompts
- injection prompts
- librarian prompts (if client keeps governance loop)

Keep anti-fabrication and output discipline intact.

### Step 5: define lifecycle contracts

- confirm frontmatter fields for briefs, drafts, final
- confirm review and approval ownership
- confirm CTA and taxonomy conventions for WordPress

### Step 6: test pipeline end-to-end

Run a dry cycle:

1. ingest one media file
2. generate derived notes
3. create brief from derived notes
4. draft article
5. run checklist and scorecard
6. validate frontmatter
7. push to WordPress draft

### Step 7: establish alignment cadence

If you want Theo Librarian equivalent for the new client:

- keep proposal-first model
- create `alignment/proposals` and `alignment/applied`
- run weekly or monthly doctrine refresh audits

## 15) Parameterization map (what changes vs what should not)

Change per client:

- brand/voice docs
- audience/offers docs
- site taxonomy defaults
- approved CTA patterns
- system prompt domain language and vocabulary

Keep stable:

- evidence hierarchy
- no-fabrication rule
- human approval gates
- final-folder semantics
- draft-first WordPress behavior
- provenance logging for injected or aligned changes

## 16) Common failure modes when cloning the system

1. Skipping derived notes and drafting directly from transcript text
2. Replacing distinctive doctrine with generic "leadership content"
3. Treating model inference as evidence
4. Writing directly to `final/` before review gates
5. Automating publish status without explicit human authorization
6. Running librarian-style edits directly against active drafts/finals
7. Omitting provenance fields on injection upgrades

## 17) Minimum operating cadence

Daily or per content item:

- ingest new source where relevant
- process transcript to derived notes
- link derived note paths in brief/draft work

Per piece:

- run checklist and scorecard
- validate frontmatter before promotion and WP sync

Weekly:

- review new source notes and outstanding draft quality issues

Monthly:

- librarian alignment pass across brand/config/prompt layers

## 18) Quickstart runbook (copy/paste)

```bash
npm install
npm run openai:ping
npm run transcribe -- --auto knowledge/source-notes/video-inbox/your-file.mp4
npm run process-transcript -- knowledge/source-notes/transcriptions/processed/your-file.md
npm run validate-frontmatter -- drafts/your-draft.md
npm run validate-frontmatter -- final/your-approved-piece.md
npm run wp:create-draft -- final/your-approved-piece.md
```

## 19) Source files to review when maintaining this system

- `README.md`
- `scripts/transcribe_video.ts`
- `scripts/process_transcript.ts`
- `scripts/validate_frontmatter.ts`
- `scripts/create_wp_draft.ts`
- `scripts/update_wp_post.ts`
- `scripts/wp_common.ts`
- `config/frontmatter_standard.md`
- `config/content_schema.md`
- `config/evidence_and_examples.md`
- `config/theo_injection_rules.md`
- `config/theo_librarian_rules.md`
- `config/email_format_rules.md`
- `workflows/editorial_workflow.md`
- `workflows/content_lifecycle.md`
- `workflows/theo_librarian_workflow.md`
- `prompts/workflow/theo_injection.md`
- `prompts/workflow/theo_injection_selective.md`
- `prompts/workflow/theo_librarian_audit.md`
- `prompts/workflow/theo_librarian_apply.md`
- `prompts/system/theo_writer_system_prompt.md`

---

If you fork this system for a new client, treat this guide as operating doctrine and update only where the new client has explicit policy differences.
