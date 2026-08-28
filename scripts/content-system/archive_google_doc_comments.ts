/**
 * Fetch Drive comments for a Google Doc and write a local JSON snapshot under
 * workspace/comment_archive/<file_id>/ (timestamped + latest.json).
 *
 * Usage (from repo root):
 *   npx tsx scripts/content-system/archive_google_doc_comments.ts [documentId|url] [--out-dir path]
 *   npx tsx scripts/content-system/archive_google_doc_comments.ts [documentId|url] --open-only
 *
 * `--open-only` — writes `*-open-only.json` / `latest-open-only.json` (unresolved only). Full snapshot unchanged.
 *
 * Default doc: Hog Eye 2026 SEO Strategy & Blueprint
 */
import "dotenv/config";
import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { google } from "googleapis";
import type { drive_v3 } from "googleapis";
import {
  createGoogleOAuthClient,
  googleDocIdFromArg,
  listAllDriveComments,
} from "./lib/google_workspace_client.js";

function isCommentOpen(c: drive_v3.Schema$Comment): boolean {
  return c.resolved !== true;
}

function serializeComment(c: drive_v3.Schema$Comment): Record<string, unknown> {
  return {
    id: c.id ?? null,
    createdTime: c.createdTime ?? null,
    resolved: c.resolved ?? null,
    author: {
      displayName: c.author?.displayName ?? null,
      emailAddress: c.author?.emailAddress ?? null,
    },
    content: c.content ?? "",
    quotedFileContent: c.quotedFileContent?.value ?? null,
    replies: (c.replies ?? []).map((r) => ({
      createdTime: r.createdTime ?? null,
      author: {
        displayName: r.author?.displayName ?? null,
        emailAddress: r.author?.emailAddress ?? null,
      },
      content: r.content ?? "",
    })),
  };
}

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  let outDirOverride: string | undefined;
  const filtered: string[] = [];
  let openOnly = false;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--out-dir" && argv[i + 1]) {
      outDirOverride = argv[i + 1];
      i++;
    } else if (argv[i] === "--open-only") {
      openOnly = true;
    } else {
      filtered.push(argv[i]!);
    }
  }
  const documentId = googleDocIdFromArg(filtered[0]);

  const authClient = await createGoogleOAuthClient([
    "https://www.googleapis.com/auth/drive.readonly",
  ]);
  const drive = google.drive({ version: "v3", auth: authClient });

  const { data: meta } = await drive.files.get({
    fileId: documentId,
    fields: "name,id",
  });
  const title = (meta as drive_v3.Schema$File).name ?? "(no title)";

  const rawComments = await listAllDriveComments(drive, documentId);
  const fetchedAt = new Date().toISOString();
  const stamp = fetchedAt.replace(/[:.]/g, "-");
  const repoRoot = process.cwd();
  const baseDir = outDirOverride
    ? resolve(outDirOverride)
    : join(repoRoot, "workspace", "comment_archive", documentId);
  mkdirSync(baseDir, { recursive: true });

  const writeSnapshot = (
    slice: drive_v3.Schema$Comment[],
    suffix: string,
    openOnlyFlag: boolean,
  ): void => {
    const comments = slice.map(serializeComment);
    const payload = {
      fetched_at: fetchedAt,
      google_doc_id: documentId,
      google_doc_title: title,
      open_only: openOnlyFlag,
      total_threads_in_doc: rawComments.length,
      comment_count: comments.length,
      comments,
    };
    const json = `${JSON.stringify(payload, null, 2)}\n`;
    const datedPath = join(baseDir, `${stamp}${suffix}.json`);
    const latestPath = join(baseDir, `latest${suffix}.json`);
    writeFileSync(datedPath, json, "utf8");
    writeFileSync(latestPath, json, "utf8");
    console.log(`Wrote ${comments.length} comments to:`);
    console.log(`  ${datedPath}`);
    console.log(`  ${latestPath}`);
  };

  writeSnapshot(rawComments, "", false);

  if (openOnly) {
    const open = rawComments.filter(isCommentOpen);
    writeSnapshot(open, "-open-only", true);
  }
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
