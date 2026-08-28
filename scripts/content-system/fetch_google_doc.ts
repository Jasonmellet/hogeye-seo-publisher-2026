/**
 * Fetch a Google Doc body (plain text) and/or Drive comments using a service account.
 * Requires: GOOGLE_APPLICATION_CREDENTIALS -> path to service account JSON key.
 * The doc must be shared with that service account's client_email.
 *
 * Usage:
 *   npx tsx scripts/content-system/fetch_google_doc.ts [documentId|full Google Doc URL]
 *   npx tsx scripts/content-system/fetch_google_doc.ts --comments-only [documentId|url]
 *   npx tsx scripts/content-system/fetch_google_doc.ts --comments-only --open-only [documentId|url]
 *
 * `--open-only` — skip threads Drive marks `resolved: true` (matches Google Docs “open comments” view).
 *
 * Local archive (JSON on disk): `npm run google:archive-comments` (add `--open-only` for `*-open-only.json`).
 */
import "dotenv/config";
import type { OAuth2Client } from "google-auth-library";
import { google } from "googleapis";
import type { drive_v3 } from "googleapis";
import {
  createGoogleOAuthClient,
  googleDocIdFromArg,
  listAllDriveComments,
} from "./lib/google_workspace_client.js";
import { plainTextFromDocumentBody } from "./lib/google_docs_plain_text.js";

function isCommentOpen(c: { resolved?: boolean | null }): boolean {
  return c.resolved !== true;
}

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  const commentsOnly = argv.includes("--comments-only");
  const openOnly = argv.includes("--open-only");
  const positional = argv.filter((a) => !a.startsWith("--"));
  const documentId = googleDocIdFromArg(positional[0]);

  const scopes = commentsOnly
    ? ["https://www.googleapis.com/auth/drive.readonly"]
    : [
        "https://www.googleapis.com/auth/documents.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
      ];

  const authClient: OAuth2Client = await createGoogleOAuthClient(scopes);
  const drive = google.drive({ version: "v3", auth: authClient });

  if (!commentsOnly) {
    const docs = google.docs({ version: "v1", auth: authClient });
    const { data: doc } = await docs.documents.get({ documentId });
    const plain = plainTextFromDocumentBody(doc);

    console.log(`Document: ${doc.title ?? "(no title)"}`);
    console.log(`ID: ${documentId}`);
    console.log(`Characters (approx): ${plain.length}\n`);
    console.log("--- Body (plain text, first 6000 chars) ---\n");
    console.log(plain.slice(0, 6000));
    if (plain.length > 6000) console.log("\n… [truncated]\n");
  } else {
    const { data: meta } = await drive.files.get({
      fileId: documentId,
      fields: "name,id",
    });
    const fileName = (meta as drive_v3.Schema$File).name;
    console.log(`Document: ${fileName ?? "(no title)"}`);
    console.log(`ID: ${documentId}\n`);
  }

  let comments = await listAllDriveComments(drive, documentId);
  const total = comments.length;
  if (openOnly) {
    comments = comments.filter(isCommentOpen);
    console.log(
      `(Open only: ${comments.length} of ${total} threads per Drive API resolved flag)\n`,
    );
  }
  console.log(`--- Drive comments (${comments.length}) ---\n`);
  for (const c of comments) {
    const who = c.author?.displayName ?? c.author?.emailAddress ?? "?";
    const when = c.createdTime ?? "";
    console.log(`[${when}] ${who}${c.resolved ? " (resolved)" : ""}`);
    if (c.quotedFileContent?.value) {
      const q = c.quotedFileContent.value;
      console.log(`  Quote: ${q.slice(0, 200)}${q.length > 200 ? "…" : ""}`);
    }
    console.log(`  ${(c.content ?? "").replace(/\n/g, "\n  ")}`);
    for (const r of c.replies ?? []) {
      const rw = r.author?.displayName ?? r.author?.emailAddress ?? "?";
      console.log(`    → ${rw}: ${r.content ?? ""}`);
    }
    console.log("");
  }
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
