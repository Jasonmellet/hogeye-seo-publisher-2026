import path from "node:path";
import { fileURLToPath } from "node:url";

import dotenv from "dotenv";

const thisDir = path.dirname(fileURLToPath(import.meta.url));

export const repoRoot = path.resolve(thisDir, "..", "..", "..");

dotenv.config({ path: path.join(repoRoot, ".env") });

/**
 * Repo-relative client workspace (content_pipeline + content_system).
 * Override with WORKSPACE_REL or HOGEYE_WORKSPACE_REL (forward slashes), e.g. `workspace`.
 */
function workspaceRoot(): string {
  const rel = process.env.WORKSPACE_REL?.trim() || process.env.HOGEYE_WORKSPACE_REL?.trim();
  if (rel) {
    const segments = rel.split("/").filter(Boolean);
    return path.join(repoRoot, ...segments);
  }
  return path.join(repoRoot, "workspace");
}

const wsRoot = workspaceRoot();

export const contentPipelineRoot = path.join(wsRoot, "content_pipeline");
export const contentSystemRoot = path.join(wsRoot, "content_system");

export const sourceRoots = {
  mediaInbox: path.join(contentPipelineRoot, "sources", "media_inbox"),
  sourceNotes: path.join(contentPipelineRoot, "sources", "source_notes"),
  transcriptsRaw: path.join(contentPipelineRoot, "sources", "transcripts", "raw"),
  transcriptsProcessed: path.join(contentPipelineRoot, "sources", "transcripts", "processed"),
  derivedNotes: path.join(contentPipelineRoot, "sources", "derived_notes")
};

export const doctrineRoots = {
  config: path.join(contentSystemRoot, "config"),
  prompts: path.join(contentSystemRoot, "prompts"),
  workflows: path.join(contentSystemRoot, "workflows"),
  alignmentProposals: path.join(contentSystemRoot, "alignment", "proposals"),
  alignmentApplied: path.join(contentSystemRoot, "alignment", "applied")
};

export function relativeToRepo(targetPath: string): string {
  return path.relative(repoRoot, targetPath).replaceAll(path.sep, "/");
}
