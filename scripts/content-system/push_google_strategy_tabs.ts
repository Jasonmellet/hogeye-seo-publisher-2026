/**
 * Push local markdown article files into Google Doc tabs (strategy blueprint doc).
 *
 * Usage:
 *   npm run google:push-tabs -- --month 2026-06 --dry-run
 *   npm run google:push-tabs -- --month 2026-06
 *   npm run google:push-tabs -- --month 2026-06 --article jun26_02
 *   npm run google:push-tabs -- --month 2026-06 --overview
 *   npm run google:push-tabs -- --month 2026-06 --no-overview
 *
 * Requires:
 * - GOOGLE_APPLICATION_CREDENTIALS (service account JSON)
 * - Doc shared with service account client_email (Editor access for writes)
 * - Google Docs API enabled on the GCP project
 * - Scope: https://www.googleapis.com/auth/documents
 */
import "dotenv/config";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { google } from "googleapis";
import type { docs_v1 } from "googleapis";
import {
  createGoogleOAuthClient,
  DEFAULT_HOGEYE_STRATEGY_GOOGLE_DOC_ID,
  googleDocIdFromArg,
} from "./lib/google_workspace_client.js";
import {
  findTabByTitleSubstring,
  listAllTabTitles,
} from "./lib/google_docs_plain_text.js";
import { contentPipelineRoot, repoRoot } from "./lib/paths.js";

type TabPushSpec = {
  articleId: string;
  tabNeedle: string;
  sourceFile: string;
};

const JUNE_OVERVIEW_TAB = {
  label: "May 2026 overview",
  tabNeedle: "May 2026",
  sourceFile: "monthly/2026-06/google_doc/COVER_PAGE_EXECUTIVE_SUMMARY.md",
};

const JUNE_TAB_PUSH: TabPushSpec[] = [
  {
    articleId: "jun26_02",
    tabNeedle: "Article 1",
    sourceFile: "monthly/2026-06/google_doc/Article_01_trapping_wild_hogs_texas.md",
  },
  {
    articleId: "jun26_01",
    tabNeedle: "Article 2",
    sourceFile: "monthly/2026-06/google_doc/Article_02_hog_trap_placement.md",
  },
  {
    articleId: "jun26_05",
    tabNeedle: "Article 3",
    sourceFile: "monthly/2026-06/google_doc/Article_03_electronic_hog_traps.md",
  },
  {
    articleId: "jun26_03",
    tabNeedle: "Article 4",
    sourceFile: "monthly/2026-06/google_doc/Article_04_multi_trap_operation.md",
  },
  {
    articleId: "jun26_04",
    tabNeedle: "Article 5",
    sourceFile: "monthly/2026-06/google_doc/Article_05_wild_hog_damage_field_guide.md",
  },
];

function parseArgs(argv: string[]): {
  documentId: string;
  month: string;
  article?: string;
  overviewOnly: boolean;
  includeOverview: boolean;
  dryRun: boolean;
} {
  let month = "";
  let article: string | undefined;
  let overviewOnly = false;
  let includeOverview = true;
  let dryRun = false;
  const positional: string[] = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "--month" && argv[i + 1]) month = argv[++i]!;
    else if (a === "--article" && argv[i + 1]) article = argv[++i]!;
    else if (a === "--overview") overviewOnly = true;
    else if (a === "--no-overview") includeOverview = false;
    else if (a === "--dry-run") dryRun = true;
    else if (!a.startsWith("--")) positional.push(a);
  }
  if (!month) throw new Error("Missing --month YYYY-MM");
  return {
    documentId: googleDocIdFromArg(positional[0]),
    month,
    article,
    overviewOnly,
    includeOverview,
    dryRun,
  };
}

function tabEndIndex(tab: docs_v1.Schema$Tab): number {
  const content = tab.documentTab?.body?.content ?? [];
  if (!content.length) return 1;
  const last = content[content.length - 1];
  return last.endIndex ?? 1;
}

/** Light markdown → plain text for Docs insert (headings stay readable). */
function markdownToPlainForDocs(raw: string): string {
  const lines = raw.replace(/\r\n/g, "\n").split("\n");
  const out: string[] = [];
  for (const line of lines) {
    if (line.startsWith("# ")) {
      out.push(line.slice(2).trim());
      out.push("");
      continue;
    }
    if (line.startsWith("## ")) {
      out.push(line.slice(3).trim());
      out.push("");
      continue;
    }
    if (line.startsWith("### ")) {
      out.push(line.slice(4).trim());
      continue;
    }
    // strip markdown links [text](url) -> text (url)
    out.push(
      line.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1 ($2)").replace(/\*\*/g, ""),
    );
  }
  return `${out.join("\n").trim()}\n`;
}

function loadSourceText(relUnderPipeline: string): string {
  const full = resolve(contentPipelineRoot, relUnderPipeline);
  return readFileSync(full, "utf8");
}

async function replaceTabText(params: {
  docs: docs_v1.Docs;
  documentId: string;
  tab: docs_v1.Schema$Tab;
  text: string;
  dryRun: boolean;
}): Promise<void> {
  const tabId = params.tab.tabProperties?.tabId;
  if (!tabId) throw new Error("Tab missing tabId");
  const end = tabEndIndex(params.tab);
  const requests: docs_v1.Schema$Request[] = [];
  if (end > 2) {
    requests.push({
      deleteContentRange: {
        range: {
          tabId,
          startIndex: 1,
          endIndex: end - 1,
        },
      },
    });
  }
  requests.push({
    insertText: {
      location: { tabId, index: 1 },
      text: params.text,
    },
  });
  if (params.dryRun) {
    console.log(
      `  [dry-run] would${end > 2 ? ` delete 1-${end - 1} then` : ""} insert ${params.text.length} chars`,
    );
    return;
  }
  await params.docs.documents.batchUpdate({
    documentId: params.documentId,
    requestBody: { requests },
  });
}

async function main(): Promise<void> {
  const { documentId, month, article, overviewOnly, includeOverview, dryRun } =
    parseArgs(process.argv.slice(2));
  if (month !== "2026-06") {
    throw new Error(`Tab push map only defined for 2026-06 (got ${month})`);
  }

  const auth = await createGoogleOAuthClient([
    "https://www.googleapis.com/auth/documents",
  ]);
  const docs = google.docs({ version: "v1", auth });
  const { data: doc } = await docs.documents.get({
    documentId,
    includeTabsContent: true,
  });

  console.log(`Document: ${doc.title ?? "(no title)"}`);
  console.log(`ID: ${documentId}`);
  console.log(`Mode: ${dryRun ? "dry-run" : "WRITE"}\n`);

  async function pushOverview(): Promise<void> {
    const tab = findTabByTitleSubstring(doc.tabs, JUNE_OVERVIEW_TAB.tabNeedle);
    if (!tab) {
      const titles = listAllTabTitles(doc);
      throw new Error(
        `No tab matched ${JSON.stringify(JUNE_OVERVIEW_TAB.tabNeedle)} for overview.\n` +
          `Available tabs (${titles.length}):\n${titles.map((t) => `  - ${t}`).join("\n")}`,
      );
    }
    const title = tab.tabProperties?.title ?? JUNE_OVERVIEW_TAB.tabNeedle;
    const plain = markdownToPlainForDocs(loadSourceText(JUNE_OVERVIEW_TAB.sourceFile));
    console.log(`→ ${JUNE_OVERVIEW_TAB.label} → tab "${title}" (${plain.length} chars)`);
    await replaceTabText({ docs, documentId, tab, text: plain, dryRun });
    console.log(`  OK`);
  }

  if (overviewOnly) {
    await pushOverview();
    console.log(dryRun ? "\nDry run complete." : "\nPushed to Google Doc.");
    return;
  }

  if (includeOverview && !article) {
    await pushOverview();
  }

  let specs = JUNE_TAB_PUSH;
  if (article) {
    specs = specs.filter((s) => s.articleId === article);
    if (!specs.length) throw new Error(`Unknown --article ${article}`);
  }

  for (const spec of specs) {
    const tab = findTabByTitleSubstring(doc.tabs, spec.tabNeedle);
    if (!tab) {
      const titles = listAllTabTitles(doc);
      throw new Error(
        `No tab matched ${JSON.stringify(spec.tabNeedle)} for ${spec.articleId}.\n` +
          `Available tabs (${titles.length}):\n${titles.map((t) => `  - ${t}`).join("\n")}`,
      );
    }
    const title = tab.tabProperties?.title ?? spec.tabNeedle;
    const plain = markdownToPlainForDocs(loadSourceText(spec.sourceFile));
    console.log(`→ ${spec.articleId} → tab "${title}" (${plain.length} chars)`);
    await replaceTabText({ docs, documentId, tab, text: plain, dryRun });
    console.log(`  OK`);
  }
  console.log(dryRun ? "\nDry run complete." : "\nPushed to Google Doc.");
}

main().catch((err: unknown) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exitCode = 1;
});
