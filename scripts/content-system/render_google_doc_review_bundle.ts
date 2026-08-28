/**
 * Merge archived **open** Drive comments + **inline** Docs suggestions into one
 * human-readable Markdown file (no API calls — run archive scripts first).
 *
 * **Default:** May publication batch (`may26_01`–`may26_05` under
 * `workspace/content_pipeline/monthly/2026-05/`) — the five client-review pieces
 * (calendar-April steering). Excludes the earlier trap batch (`apr26_*` in
 * `2026-04/`, March research / April go-live trap SOPs). Use `--full` for everything.
 *
 * Usage (repo root):
 *   npx tsx scripts/content-system/render_google_doc_review_bundle.ts [documentId|url]
 *   npx tsx scripts/content-system/render_google_doc_review_bundle.ts --full [documentId|url]
 *
 * Reads:
 *   workspace/comment_archive/<id>/latest-open-only.json
 *   workspace/comment_archive/<id>/suggestions-latest.json
 *
 * Writes:
 *   workspace/comment_archive/<id>/REVIEW_BUNDLE_LATEST.md (default: may26_01–may26_05)
 *   workspace/comment_archive/<id>/REVIEW_BUNDLE_FULL.md (with `--full` only)
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { googleDocIdFromArg } from "./lib/google_workspace_client.js";
import type { DocSuggestionSnippet } from "./lib/google_docs_suggestions.js";

/**
 * `may26_01` … `may26_05` — CONTENT_REGISTRY titles / strategy-doc anchors.
 * (Not `apr26_*`: that batch is the trap SOP package under `2026-04/`.)
 */
const MAY_PUBLICATION_BATCH_COMMENT_NEEDLES = [
  "how much do feral hogs cost you",
  "damage by crop, region, and herd size",
  "wild hog behavior",
  "how they scout",
  "the hog trap baiting guide",
  "hog trap baiting guide",
  "common hog trap mistakes",
  "corral trap vs. box trap vs. drop net",
  "which hog trap is right for your property",
] as const;

/** Docs tab title substrings in `section` from `documents.get` (numbered tabs in strategy doc). */
const MAY_PUBLICATION_BATCH_SUGGESTION_SECTION_NEEDLES = [
  "how much do feral hogs cost you", // e.g. "(1: How Much Do Feral Hogs Cost You?)"
  "common hog trap mistakes", // "(4: Common Hog Trap Mistakes)"
  "corral trap vs. box trap vs. drop net", // "(5: Corral Trap vs. …)"
] as const;

type ArchivedReply = {
  createdTime: string | null;
  author: { displayName: string | null; emailAddress: string | null };
  content: string;
};

type ArchivedComment = {
  id: string | null;
  createdTime: string | null;
  resolved: boolean | null;
  author: { displayName: string | null; emailAddress: string | null };
  content: string;
  quotedFileContent: string | null;
  replies: ArchivedReply[];
};

type OpenOnlyPayload = {
  fetched_at: string;
  google_doc_id: string;
  google_doc_title: string;
  open_only?: boolean;
  total_threads_in_doc?: number;
  comment_count: number;
  comments: ArchivedComment[];
};

type SuggestionsPayload = {
  fetched_at: string;
  google_doc_id: string;
  google_doc_title: string;
  suggestions_view_mode?: string;
  suggestion_snippet_count: number;
  suggestions: DocSuggestionSnippet[];
};

function commentMatchesMayPublicationBatch(c: ArchivedComment): boolean {
  const hay = `${c.quotedFileContent ?? ""}\n${c.content ?? ""}`.toLowerCase();
  return MAY_PUBLICATION_BATCH_COMMENT_NEEDLES.some((n) => hay.includes(n));
}

function suggestionMatchesMayPublicationBatch(s: DocSuggestionSnippet): boolean {
  const sec = s.section.toLowerCase();
  return MAY_PUBLICATION_BATCH_SUGGESTION_SECTION_NEEDLES.some((n) =>
    sec.includes(n),
  );
}

function fence(text: string): string {
  const fenceChar = "`";
  const longest = text.match(/`{3,}/);
  const inner = longest ? longest[0].length + 1 : 3;
  const f = fenceChar.repeat(inner);
  return `${f}\n${text.replace(/\r\n/g, "\n")}\n${f}`;
}

function formatComments(
  comments: ArchivedComment[],
  emptyBlurb?: string,
): string {
  if (!comments.length) {
    return (
      (emptyBlurb ?? "*No open comments in `latest-open-only.json`.*") + "\n\n"
    );
  }
  let md = "";
  for (const c of comments) {
    const id = c.id ?? "(no id)";
    const when = c.createdTime ?? "";
    const who =
      [c.author?.displayName, c.author?.emailAddress].filter(Boolean).join(" · ") ||
      "(unknown author)";
    md += `### ${id} — ${when}\n\n`;
    md += `**Author:** ${who}\n\n`;
    if (c.quotedFileContent) {
      md += "**Anchored quote (from Doc):**\n\n";
      for (const line of c.quotedFileContent.split("\n")) {
        md += `> ${line}\n`;
      }
      md += "\n";
    }
    md += "**Comment:**\n\n";
    md += `${fence(c.content ?? "")}\n\n`;
    if (c.replies?.length) {
      md += "**Replies:**\n\n";
      for (const r of c.replies) {
        const rw = [r.author?.displayName, r.author?.emailAddress]
          .filter(Boolean)
          .join(" · ");
        md += `**Reply** (${r.createdTime ?? ""}) — ${rw || "unknown"}:\n\n`;
        md += `${fence(r.content ?? "")}\n\n`;
      }
    }
    md += "---\n\n";
  }
  return md;
}

function formatSuggestions(
  rows: DocSuggestionSnippet[],
  emptyBlurb?: string,
): string {
  if (!rows.length) {
    return (
      (emptyBlurb ?? "*No inline suggestions in `suggestions-latest.json`.*") + "\n\n"
    );
  }
  let md = "";
  let cur = "";
  for (const r of rows) {
    const key = `${r.kind}:${r.suggestionId}`;
    if (key !== cur) {
      cur = key;
      md += `#### ${r.kind} — \`${r.suggestionId}\`\n\n`;
    }
    md += `- **${r.section}** @ ${r.startIndex ?? "?"}–${r.endIndex ?? "?"}: ${JSON.stringify(r.content)}\n`;
  }
  md += "\n";
  return md;
}

function main(): void {
  const argv = process.argv.slice(2);
  let fullDoc = false;
  const positional: string[] = [];
  for (const a of argv) {
    if (a === "--full") fullDoc = true;
    else positional.push(a);
  }
  const documentId = googleDocIdFromArg(positional[0]);

  const repoRoot = process.cwd();
  const dir = join(repoRoot, "workspace", "comment_archive", documentId);
  const openPath = join(dir, "latest-open-only.json");
  const sugPath = join(dir, "suggestions-latest.json");
  const outPath = join(
    dir,
    fullDoc ? "REVIEW_BUNDLE_FULL.md" : "REVIEW_BUNDLE_LATEST.md",
  );

  let openRaw: string;
  let sugRaw: string;
  try {
    openRaw = readFileSync(openPath, "utf8");
  } catch {
    console.error(
      `Missing ${openPath}\nRun: npm run google:archive-comments-open -- "${documentId}"`,
    );
    process.exitCode = 1;
    return;
  }
  try {
    sugRaw = readFileSync(sugPath, "utf8");
  } catch {
    console.error(
      `Missing ${sugPath}\nRun: npm run google:archive-suggestions -- "${documentId}"`,
    );
    process.exitCode = 1;
    return;
  }

  const open = JSON.parse(openRaw) as OpenOnlyPayload;
  const sug = JSON.parse(sugRaw) as SuggestionsPayload;
  const allComments = open.comments ?? [];
  const allSugs = sug.suggestions ?? [];

  const comments = fullDoc
    ? allComments
    : allComments.filter(commentMatchesMayPublicationBatch);
  const sugs = fullDoc
    ? allSugs
    : allSugs.filter(suggestionMatchesMayPublicationBatch);

  const title = open.google_doc_title || sug.google_doc_title || "(no title)";
  const builtAt = new Date().toISOString();
  const totalInDoc = open.total_threads_in_doc;

  let md = `# Client review bundle\n\n`;
  md += `**Document name:** ${title}\n\n`;
  md += `**Google file ID:** \`${documentId}\`\n\n`;
  md += `**Open in Docs:** https://docs.google.com/document/d/${documentId}/edit\n\n`;
  md += `**This bundle generated:** ${builtAt}\n\n`;
  if (fullDoc) {
    md +=
      `**Scope:** **Full strategy doc** (all open comments + all suggestion snippets). ` +
      `For the five-piece \`may26_01\`–\`may26_05\` batch only, run without \`--full\`.\n\n`;
  } else {
    md +=
      `**Scope:** **May publication batch** — \`may26_01\` … \`may26_05\` (\`workspace/content_pipeline/monthly/2026-05/\`). ` +
      `This is the client-review set you are steering in **calendar April** (per registry: distinct from the \`apr26_*\` trap SOPs in \`2026-04/\`). ` +
      `Comments: anchor/body match those five titles. Suggestions: Docs tabs \`1:\` damage, \`4:\` mistakes, \`5:\` trap comparison (add tab needles when pieces 2–3 get their own tabs). ` +
      `Full doc: \`npm run google:render-review-bundle-full\` → \`REVIEW_BUNDLE_FULL.md\`.\n\n`;
  }
  md += `| Source | Fetched (archive run) | In this file |\n`;
  md += `|--------|------------------------|----------------|\n`;
  if (fullDoc) {
    md += `| Open Drive comments | ${open.fetched_at} | **${comments.length}** open |\n`;
    md += `| Inline Docs suggestions | ${sug.fetched_at} | **${sugs.length}** snippets`;
    if (sug.suggestions_view_mode) {
      md += ` (\`${sug.suggestions_view_mode}\`)`;
    }
    md += ` |\n`;
    if (totalInDoc !== undefined) {
      md += `| *(reference)* threads in last full pull | — | ${totalInDoc} total |\n`;
    }
  } else {
    md += `| Open Drive comments | ${open.fetched_at} | **${comments.length}** (may26 batch match) of **${allComments.length}** open in archive |\n`;
    md += `| Inline Docs suggestions | ${sug.fetched_at} | **${sugs.length}** (may26 tab match) of **${allSugs.length}** in archive`;
    if (sug.suggestions_view_mode) {
      md += ` (\`${sug.suggestions_view_mode}\`)`;
    }
    md += ` |\n`;
  }
  md += `\n`;
  md += `---\n\n`;
  md += `## 1. Open comments (margin threads)\n\n`;
  md += formatComments(
    comments,
    !fullDoc && !comments.length
      ? "*No open comments matched the may26_01–may26_05 title filters. Run with --full for the entire open set, or extend MAY_PUBLICATION_BATCH_COMMENT_NEEDLES in render_google_doc_review_bundle.ts.*"
      : undefined,
  );
  md += `---\n\n`;
  md += `## 2. Inline suggestions (Suggesting mode — insert/delete IDs)\n\n`;
  md += `*Snippets list \`section\` (tab title in the Doc) so you can map back to drafts.*\n\n`;
  md += formatSuggestions(
    sugs,
    !fullDoc && !sugs.length
      ? "*No inline suggestions on the may26 Docs tabs in this snapshot (or none pending). Run with --full for all tabs.*"
      : undefined,
  );

  writeFileSync(outPath, md, "utf8");
  console.log(
    fullDoc
      ? `Wrote ${outPath} (full doc: ${comments.length} comments, ${sugs.length} snippets)`
      : `Wrote ${outPath} (may26 batch: ${comments.length} comments, ${sugs.length} snippets)`,
  );
}

main();
