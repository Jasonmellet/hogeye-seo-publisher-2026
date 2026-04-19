import fs from "node:fs/promises";
import path from "node:path";

import matter from "gray-matter";

import { contentPipelineRoot, contentSystemRoot, relativeToRepo, sourceRoots } from "./paths.js";
import { compactTimestamp, readUtf8, writeUtf8 } from "./runtime.js";

export type Confidence = "high" | "medium" | "low";
export type UpdateType = "add" | "strengthen" | "reconcile" | "remove" | "no-change";
export type ProposalStatus = "pending" | "approved" | "rejected";

export type LibrarianItem = {
  id: string;
  status: ProposalStatus;
  target_file: string;
  update_type: UpdateType;
  title: string;
  rationale: string;
  source_paths: string[];
  confidence: Confidence;
  overreach_check: string;
  proposed_content: string;
};

export type LibrarianProposal = {
  proposal_id: string;
  created_at: string;
  scope: string;
  rules_version: string;
  source_count: number;
  sources: string[];
  items: LibrarianItem[];
};

const ALLOWED_TARGETS = [
  path.join(contentPipelineRoot, "HUMANIZER_STYLE_GUIDE.md"),
  path.join(contentPipelineRoot, "templates", "research_pack.template.md"),
  path.join(contentPipelineRoot, "templates", "draft.template.md"),
  path.join(contentSystemRoot, "config", "evidence_and_truth.md"),
  path.join(contentSystemRoot, "prompts", "workflow", "draft_article.md"),
  path.join(contentSystemRoot, "workflows", "editorial_workflow.md")
];

export function getAllowedTargets(): string[] {
  return [...ALLOWED_TARGETS];
}

export async function getDerivedNotePaths(limit = 20): Promise<string[]> {
  const files = await fs.readdir(sourceRoots.derivedNotes);
  return files
    .filter((f) => f.endsWith(".md") && f.toLowerCase() !== "readme.md")
    .sort()
    .reverse()
    .slice(0, limit)
    .map((f) => path.join(sourceRoots.derivedNotes, f));
}

export async function buildDerivedNoteDigest(paths: string[]): Promise<string> {
  const sections: string[] = [];
  for (const p of paths) {
    const raw = await readUtf8(p);
    const parsed = matter(raw);
    const title = String(parsed.data.title || path.basename(p));
    const sample = parsed.content
      .split("\n")
      .filter((line) => line.trim().startsWith("- "))
      .slice(0, 16)
      .join("\n");
    sections.push(
      [
        `## Source: ${title}`,
        `path: ${relativeToRepo(p)}`,
        "",
        sample || "_No bullet summary found_"
      ].join("\n")
    );
  }
  return sections.join("\n\n");
}

export function validateProposal(proposal: LibrarianProposal): void {
  const allowed = new Set(getAllowedTargets().map((p) => path.resolve(p)));
  for (const item of proposal.items) {
    const target = path.resolve(item.target_file);
    if (!allowed.has(target)) {
      throw new Error(`Proposal item ${item.id} targets disallowed path: ${item.target_file}`);
    }
  }
}

export function proposalJsonPath(proposalId: string): string {
  return path.join(contentSystemRoot, "alignment", "proposals", `${proposalId}.json`);
}

export function proposalMdPath(proposalId: string): string {
  return path.join(contentSystemRoot, "alignment", "proposals", `${proposalId}.md`);
}

export function appliedJsonPath(proposalId: string): string {
  return path.join(contentSystemRoot, "alignment", "applied", `${proposalId}.applied.json`);
}

export function appliedMdPath(proposalId: string): string {
  return path.join(contentSystemRoot, "alignment", "applied", `${proposalId}.applied.md`);
}

export function newProposalId(): string {
  return `${compactTimestamp()}_librarian_audit`;
}

export async function writeProposalArtifacts(proposal: LibrarianProposal): Promise<{ jsonPath: string; mdPath: string }> {
  const jsonPath = proposalJsonPath(proposal.proposal_id);
  const mdPath = proposalMdPath(proposal.proposal_id);

  await writeUtf8(jsonPath, `${JSON.stringify(proposal, null, 2)}\n`);

  const lines: string[] = [];
  lines.push(`# Librarian Proposal: ${proposal.proposal_id}`);
  lines.push("");
  lines.push(`- created_at: ${proposal.created_at}`);
  lines.push(`- scope: ${proposal.scope}`);
  lines.push(`- source_count: ${proposal.source_count}`);
  lines.push("");
  lines.push("## Sources");
  lines.push("");
  for (const src of proposal.sources) {
    lines.push(`- \`${src}\``);
  }
  lines.push("");
  lines.push("## Proposed items");
  lines.push("");
  for (const item of proposal.items) {
    lines.push(`### ${item.id}: ${item.title}`);
    lines.push("");
    lines.push(`- status: ${item.status}`);
    lines.push(`- target_file: \`${relativeToRepo(item.target_file)}\``);
    lines.push(`- update_type: ${item.update_type}`);
    lines.push(`- confidence: ${item.confidence}`);
    lines.push(`- rationale: ${item.rationale}`);
    lines.push(`- overreach_check: ${item.overreach_check}`);
    lines.push("");
    lines.push("```md");
    lines.push(item.proposed_content.trim());
    lines.push("```");
    lines.push("");
  }

  await writeUtf8(mdPath, `${lines.join("\n")}\n`);
  return { jsonPath, mdPath };
}
