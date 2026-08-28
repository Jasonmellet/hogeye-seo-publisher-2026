import { existsSync } from "node:fs";
import { resolve } from "node:path";
import type { OAuth2Client } from "google-auth-library";
import { google } from "googleapis";
import type { drive_v3 } from "googleapis";

/** Default: Hog Eye | 2026 SEO Strategy & Blueprint */
export const DEFAULT_HOGEYE_STRATEGY_GOOGLE_DOC_ID =
  "1BcRBkePhe2XFHpZuF9CorPJU-6hcfW0qXyt5iGYyW_Y";

export function googleDocIdFromArg(raw: string | undefined): string {
  if (!raw?.trim()) return DEFAULT_HOGEYE_STRATEGY_GOOGLE_DOC_ID;
  const trimmed = raw.trim();
  const m = trimmed.match(/\/d\/([a-zA-Z0-9_-]+)/);
  if (m?.[1]) return m[1];
  return trimmed;
}

/** Absolute path to service account JSON; throws if missing. */
export function resolveGoogleServiceAccountKeyPath(): string {
  const keyPath = process.env.GOOGLE_APPLICATION_CREDENTIALS?.trim();
  if (!keyPath) {
    throw new Error(
      "Set GOOGLE_APPLICATION_CREDENTIALS in .env to your service account JSON key path.",
    );
  }
  const absoluteKey = resolve(keyPath);
  if (!existsSync(absoluteKey)) {
    throw new Error(
      `Service account key file not found:\n  ${absoluteKey}\n` +
        "Update .env to a path that exists on this machine.",
    );
  }
  return absoluteKey;
}

export async function createGoogleOAuthClient(
  scopes: string[],
): Promise<OAuth2Client> {
  const auth = new google.auth.GoogleAuth({
    keyFile: resolveGoogleServiceAccountKeyPath(),
    scopes,
  });
  return (await auth.getClient()) as OAuth2Client;
}

export async function listAllDriveComments(
  drive: drive_v3.Drive,
  fileId: string,
): Promise<NonNullable<drive_v3.Schema$Comment>[]> {
  const out: NonNullable<drive_v3.Schema$Comment>[] = [];
  let pageToken: string | undefined;
  const fields =
    "nextPageToken, comments(id,author(displayName,emailAddress),content,resolved,deleted,createdTime,quotedFileContent(value),replies(author(displayName,emailAddress),content,createdTime))";
  do {
    const { data } = await drive.comments.list({
      fileId,
      pageSize: 100,
      pageToken,
      fields,
    });
    for (const c of data.comments ?? []) {
      if (c && !c.deleted) out.push(c);
    }
    pageToken = data.nextPageToken ?? undefined;
  } while (pageToken);
  return out;
}
