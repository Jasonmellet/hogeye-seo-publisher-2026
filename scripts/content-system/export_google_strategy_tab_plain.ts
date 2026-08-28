/**
 * Pull **saved** Google Doc text for one **tab** (plain text) after client review.
 * Uses default `documents.get` (not `SUGGESTIONS_INLINE`), so **accepted**
 * suggestions are already reflected in the payload.
 *
 * Use this when Google is canonical and you need a local file to reconcile
 * `may26_*_draft.md` (headings, lists, and frontmatter still need human/agent pass).
 *
 * Usage (repo root):
 *   npx tsx scripts/content-system/export_google_strategy_tab_plain.ts \
 *     --tab "Wild Hog Behavior" \
 *     --out workspace/content_pipeline/monthly/2026-05/drafts/_google_sync/may26_02_plain.txt \
 *     [documentId|url]
 *
 * Requires: GOOGLE_APPLICATION_CREDENTIALS, `includeTabsContent: true`.
 */
import "dotenv/config";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { google } from "googleapis";
import type { docs_v1 } from "googleapis";
import {
  createGoogleOAuthClient,
  googleDocIdFromArg,
} from "./lib/google_workspace_client.js";
import {
  findTabByTitleSubstring,
  listAllTabTitles,
  plainTextFromDocumentTab,
} from "./lib/google_docs_plain_text.js";

function parseArgs(argv: string[]): {
  documentId: string;
  tabNeedle: string;
  outPath: string;
} {
  let tabNeedle = "";
  let outPath = "";
  const positional: string[] = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "--tab" && argv[i + 1]) {
      tabNeedle = argv[++i]!;
    } else if (a === "--out" && argv[i + 1]) {
      outPath = argv[++i]!;
    } else if (!a.startsWith("--")) {
      positional.push(a);
    }
  }
  if (!tabNeedle.trim()) {
    throw new Error('Missing --tab "substring of tab title (e.g. Wild Hog Behavior)"');
  }
  if (!outPath.trim()) {
    throw new Error("Missing --out path/to/file.txt");
  }
  return {
    documentId: googleDocIdFromArg(positional[0]),
    tabNeedle,
    outPath,
  };
}

async function main(): Promise<void> {
  const { documentId, tabNeedle, outPath } = parseArgs(process.argv.slice(2));
  const authClient = await createGoogleOAuthClient([
    "https://www.googleapis.com/auth/documents.readonly",
  ]);
  const docs = google.docs({ version: "v1", auth: authClient });
  const { data } = await docs.documents.get({
    documentId,
    includeTabsContent: true,
  });
  const doc = data as docs_v1.Schema$Document;
  const tab = findTabByTitleSubstring(doc.tabs, tabNeedle);
  if (!tab) {
    const titles = listAllTabTitles(doc);
    console.error(
      `No tab matched --tab ${JSON.stringify(tabNeedle)}.\n` +
        `Tab titles in this document (${titles.length}):\n` +
        titles.map((t) => `  - ${t}`).join("\n"),
    );
    process.exitCode = 1;
    return;
  }
  const tabTitle = tab.tabProperties?.title ?? "(untitled tab)";
  const plain = plainTextFromDocumentTab(tab);
  const pulledAt = new Date().toISOString();
  const header =
    `# Google Doc tab export (plain text)\n\n` +
    `**Pulled:** ${pulledAt}\n` +
    `**Document:** ${doc.title ?? ""}\n` +
    `**documentId:** \`${documentId}\`\n` +
    `**Tab matched:** ${JSON.stringify(tabTitle)} (needle ${JSON.stringify(tabNeedle)})\n\n` +
    `---\n\n`;

  const absoluteOut = resolve(process.cwd(), outPath);
  mkdirSync(dirname(absoluteOut), { recursive: true });
  writeFileSync(absoluteOut, header + plain, "utf8");
  console.log(`Wrote ${plain.length} characters of body text to:\n  ${absoluteOut}`);
}

main().catch((e: unknown) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exitCode = 1;
});
