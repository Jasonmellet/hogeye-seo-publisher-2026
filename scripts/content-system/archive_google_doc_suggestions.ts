/**
 * Fetch Google Docs **suggesting-mode** edits via documents.get with
 * suggestionsViewMode=SUGGESTIONS_INLINE.
 *
 * Collects `suggestedInsertionIds` / `suggestedDeletionIds` (and inline-object
 * insertion IDs) on **text runs**, other **paragraph elements** (person links,
 * rich links, breaks, …), **structural** nodes (section breaks, tables/rows/cells,
 * TOC), each tab’s **headers / footers / footnotes**, and **inline / positioned**
 * object maps.
 *
 * Complements Drive `comments.list` (margin comments). Suggestion UI labels like
 * "Replace:" / "Add:" map to these structural IDs, not to Drive comments.
 *
 * Usage (repo root):
 *   npx tsx scripts/content-system/archive_google_doc_suggestions.ts [documentId|url]
 *
 * Output:
 *   workspace/comment_archive/<file_id>/suggestions-latest.json
 *   workspace/comment_archive/<file_id>/suggestions-<ISO-stamp>.json
 *   workspace/comment_archive/<file_id>/SUGGESTIONS_LATEST.md
 *
 * Requires: GOOGLE_APPLICATION_CREDENTIALS, Docs API enabled, service account can
 * **view** suggestions (403 if commenter-only without suggestion visibility).
 */
import "dotenv/config";
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { google } from "googleapis";
import type { docs_v1 } from "googleapis";
import {
  createGoogleOAuthClient,
  googleDocIdFromArg,
} from "./lib/google_workspace_client.js";
import {
  extractSuggestionSnippets,
  type DocSuggestionSnippet,
} from "./lib/google_docs_suggestions.js";

function buildMarkdown(
  title: string,
  documentId: string,
  fetchedAt: string,
  rows: DocSuggestionSnippet[],
): string {
  let md = `# Google Doc suggestions (inline)\n\n`;
  md += `**Document:** ${title}\n`;
  md += `**file_id / documentId:** \`${documentId}\`\n`;
  md += `**Fetched:** ${fetchedAt}\n`;
  md += `**Edit link:** https://docs.google.com/document/d/${documentId}/edit\n\n`;
  md += `**Total suggestion snippets:** ${rows.length}\n\n`;
  md += `---\n\n`;
  if (!rows.length) {
    md += `*(No \`suggestedInsertionIds\` / \`suggestedDeletionIds\` in this response — either no pending suggestions, or the account cannot read suggestion mode — see JSON stderr from script run.)*\n`;
    return md;
  }
  let cur = "";
  for (const r of rows) {
    const key = `${r.kind}:${r.suggestionId}`;
    if (key !== cur) {
      cur = key;
      md += `## ${r.kind} — \`${r.suggestionId}\`\n\n`;
    }
    md += `- **${r.section}** @ ${r.startIndex ?? "?"}–${r.endIndex ?? "?"}: ${JSON.stringify(r.content)}\n`;
  }
  md += "\n";
  return md;
}

async function main(): Promise<void> {
  const documentId = googleDocIdFromArg(process.argv[2]);

  const authClient = await createGoogleOAuthClient([
    "https://www.googleapis.com/auth/documents.readonly",
  ]);
  const docs = google.docs({ version: "v1", auth: authClient });

  let doc: docs_v1.Schema$Document;
  try {
    const res = await docs.documents.get({
      documentId,
      suggestionsViewMode: "SUGGESTIONS_INLINE",
      includeTabsContent: true,
    });
    doc = res.data as docs_v1.Schema$Document;
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    if (msg.includes("403")) {
      console.error(
        "Docs API returned 403 for SUGGESTIONS_INLINE. The service account may need broader access, or Google may restrict suggestion visibility for this doc.",
      );
    }
    throw e;
  }

  const title = doc.title ?? "(no title)";
  const rows = extractSuggestionSnippets(doc);
  const fetchedAt = new Date().toISOString();
  const stamp = fetchedAt.replace(/[:.]/g, "-");
  const repoRoot = process.cwd();
  const baseDir = join(repoRoot, "workspace", "comment_archive", documentId);
  mkdirSync(baseDir, { recursive: true });

  const payload = {
    fetched_at: fetchedAt,
    google_doc_id: documentId,
    google_doc_title: title,
    suggestions_view_mode: "SUGGESTIONS_INLINE",
    suggestion_snippet_count: rows.length,
    suggestions: rows,
  };

  const json = `${JSON.stringify(payload, null, 2)}\n`;
  const jsonPath = join(baseDir, `suggestions-${stamp}.json`);
  const latestJson = join(baseDir, "suggestions-latest.json");
  writeFileSync(jsonPath, json, "utf8");
  writeFileSync(latestJson, json, "utf8");

  const md = buildMarkdown(title, documentId, fetchedAt, rows);
  const mdPath = join(baseDir, "SUGGESTIONS_LATEST.md");
  writeFileSync(mdPath, md, "utf8");

  console.log(`Suggestion snippets: ${rows.length}`);
  console.log(`  ${jsonPath}`);
  console.log(`  ${latestJson}`);
  console.log(`  ${mdPath}`);
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
