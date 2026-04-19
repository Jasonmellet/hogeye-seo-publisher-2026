import path from "node:path";

import {
  appliedJsonPath,
  appliedMdPath,
  LibrarianItem,
  LibrarianProposal,
  validateProposal
} from "./lib/librarian.js";
import { readUtf8, writeUtf8 } from "./lib/runtime.js";

function parseArgs(): { proposalPath: string; applyAllPending: boolean; onlyIds: Set<string> } {
  const args = process.argv.slice(2);
  const proposalIndex = args.indexOf("--proposal");
  const proposalPath = proposalIndex >= 0 && args[proposalIndex + 1] ? path.resolve(args[proposalIndex + 1]) : "";

  const applyAllPending = args.includes("--apply-all-pending");
  const idsIndex = args.indexOf("--ids");
  const onlyIds = new Set<string>();
  if (idsIndex >= 0 && args[idsIndex + 1]) {
    for (const id of args[idsIndex + 1].split(",")) {
      const trimmed = id.trim();
      if (trimmed) onlyIds.add(trimmed);
    }
  }
  return { proposalPath, applyAllPending, onlyIds };
}

function shouldApply(item: LibrarianItem, applyAllPending: boolean, onlyIds: Set<string>): boolean {
  if (onlyIds.size > 0) {
    return onlyIds.has(item.id);
  }
  if (applyAllPending) {
    return item.status === "pending" || item.status === "approved";
  }
  return item.status === "approved";
}

async function appendUpdateToTarget(item: LibrarianItem, proposalId: string): Promise<void> {
  const targetPath = path.resolve(item.target_file);
  const current = await readUtf8(targetPath);
  const block = [
    "",
    "## Librarian Applied Updates",
    "",
    `- proposal_id: ${proposalId}`,
    `- item_id: ${item.id}`,
    `- applied_at: ${new Date().toISOString()}`,
    "",
    item.proposed_content.trim(),
    ""
  ].join("\n");
  await writeUtf8(targetPath, `${current.trimEnd()}\n${block}`);
}

async function main(): Promise<void> {
  const { proposalPath, applyAllPending, onlyIds } = parseArgs();
  if (!proposalPath) {
    throw new Error(
      "Usage: npm run librarian:apply -- --proposal <proposal.json> [--apply-all-pending] [--ids item_01,item_02]"
    );
  }

  const proposal = JSON.parse(await readUtf8(proposalPath)) as LibrarianProposal;
  validateProposal(proposal);

  const selected = proposal.items.filter((item) => shouldApply(item, applyAllPending, onlyIds));
  if (selected.length === 0) {
    throw new Error("No proposal items selected for apply. Mark items approved or pass --apply-all-pending/--ids.");
  }

  for (const item of selected) {
    await appendUpdateToTarget(item, proposal.proposal_id);
  }

  const appliedRecord = {
    proposal_id: proposal.proposal_id,
    applied_at: new Date().toISOString(),
    source_proposal_json: proposalPath,
    applied_items: selected.map((item) => ({
      id: item.id,
      target_file: item.target_file,
      update_type: item.update_type,
      title: item.title
    }))
  };

  const appliedJson = appliedJsonPath(proposal.proposal_id);
  const appliedMd = appliedMdPath(proposal.proposal_id);
  await writeUtf8(appliedJson, `${JSON.stringify(appliedRecord, null, 2)}\n`);
  await writeUtf8(
    appliedMd,
    [
      `# Librarian Applied Log: ${proposal.proposal_id}`,
      "",
      `- applied_at: ${appliedRecord.applied_at}`,
      `- source_proposal_json: ${proposalPath}`,
      "",
      "## Applied items",
      "",
      ...appliedRecord.applied_items.map(
        (item) => `- ${item.id}: ${item.title} -> \`${item.target_file}\` (${item.update_type})`
      ),
      ""
    ].join("\n")
  );

  console.log(`OK applied items: ${selected.length}`);
  console.log(`OK applied log json: ${appliedJson}`);
  console.log(`OK applied log md: ${appliedMd}`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
