import path from "node:path";

import { generateMarkdownFromPrompt } from "./lib/openai.js";
import {
  buildDerivedNoteDigest,
  getAllowedTargets,
  getDerivedNotePaths,
  LibrarianProposal,
  newProposalId,
  validateProposal,
  writeProposalArtifacts
} from "./lib/librarian.js";

function parseLimitArg(): number {
  const idx = process.argv.indexOf("--limit");
  if (idx === -1) {
    return 10;
  }
  const raw = process.argv[idx + 1];
  const parsed = Number.parseInt(raw || "", 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error("Invalid --limit value; expected positive integer.");
  }
  return parsed;
}

function buildSystemPrompt(): string {
  return [
    "You are the HogEye Librarian audit engine.",
    "Generate a conservative proposal for updating shared doctrine docs from derived notes.",
    "Rules:",
    "- Update only allowed target files.",
    "- Never target active monthly drafts, briefs, research packs, or QA files.",
    "- Use exact product naming: HogEye (never Hawkeye/Hawgeye).",
    "- Prefer strengthen/reconcile over add/remove when uncertain.",
    "- Do not invent facts; only propose language/process updates supported by the provided derived-note digest.",
    "- Keep proposal items concise and implementable.",
    "",
    "Return JSON only with this exact shape:",
    "{",
    '  "scope": "string",',
    '  "rules_version": "string",',
    '  "items": [',
    "    {",
    '      "id": "string",',
    '      "status": "pending",',
    '      "target_file": "absolute path from allowed list",',
    '      "update_type": "add|strengthen|reconcile|remove|no-change",',
    '      "title": "string",',
    '      "rationale": "string",',
    '      "source_paths": ["repo-relative-path", "..."],',
    '      "confidence": "high|medium|low",',
    '      "overreach_check": "string",',
    '      "proposed_content": "markdown snippet to append or merge"', 
    "    }",
    "  ]",
    "}",
    "",
    "If uncertain, return fewer items rather than broad or risky edits."
  ].join("\n");
}

function fallbackProposal(params: {
  proposalId: string;
  sources: string[];
  allowedTargets: string[];
}): LibrarianProposal {
  const [humanizer, researchTemplate, draftPrompt] = params.allowedTargets;
  return {
    proposal_id: params.proposalId,
    created_at: new Date().toISOString(),
    scope: "Fallback conservative librarian proposal from derived-note patterns",
    rules_version: "hogeye-librarian-v1",
    source_count: params.sources.length,
    sources: params.sources,
    items: [
      {
        id: "item_01",
        status: "pending",
        target_file: humanizer,
        update_type: "strengthen",
        title: "Strengthen connection-integrity voice guidance",
        rationale: "Derived notes repeatedly stress cable checks, indicator lights, and trigger readiness.",
        source_paths: params.sources.slice(0, 4),
        confidence: "medium",
        overreach_check: "Adds writing guidance only; no new product claims.",
        proposed_content:
          "## Video-series delta (connection integrity)\n\n- Prefer practical wording around indicator-light checks, cable seating, and trigger-readiness confirmation.\n- Keep setup language procedural and field-specific.\n- Do not introduce new numeric performance claims."
      },
      {
        id: "item_02",
        status: "pending",
        target_file: researchTemplate,
        update_type: "strengthen",
        title: "Capture derived-note influence explicitly",
        rationale: "Recent source set provides strong SOP and troubleshooting structure for briefs/drafts.",
        source_paths: params.sources,
        confidence: "high",
        overreach_check: "Template expansion only.",
        proposed_content:
          "- setup/troubleshooting patterns extracted from derived notes:\n- indicator-light logic used:\n- trigger-readiness checks referenced:"
      },
      {
        id: "item_03",
        status: "pending",
        target_file: draftPrompt,
        update_type: "strengthen",
        title: "Prefer procedural trap-operations framing",
        rationale: "Derived notes improve draft quality when emphasizing sequence and reliability checks.",
        source_paths: params.sources.slice(0, 3),
        confidence: "medium",
        overreach_check: "Prompt-level behavior; no factual claims added.",
        proposed_content:
          "- Favor sequence-based sections: setup, verify, trigger, confirm.\n- Include troubleshooting checkpoints where source-supported.\n- Keep every section tied to trap outcomes, not generic monitoring."
      }
    ]
  };
}

async function main(): Promise<void> {
  const limit = parseLimitArg();
  const notePaths = await getDerivedNotePaths(limit);
  if (notePaths.length === 0) {
    throw new Error("No derived notes found for librarian audit.");
  }

  const allowedTargets = getAllowedTargets();
  const sourceRelPaths = notePaths.map((p) => p.replaceAll(path.sep, "/"));
  const digest = await buildDerivedNoteDigest(notePaths);
  const proposalId = newProposalId();

  let proposal: LibrarianProposal;
  try {
    const response = await generateMarkdownFromPrompt({
      system: buildSystemPrompt(),
      user: [
        `Allowed target files:\n${allowedTargets.map((t) => `- ${path.resolve(t)}`).join("\n")}`,
        "",
        `Derived-note sources:\n${sourceRelPaths.map((s) => `- ${s}`).join("\n")}`,
        "",
        "Derived-note digest:",
        digest
      ].join("\n")
    });
    const parsed = JSON.parse(response) as Omit<LibrarianProposal, "proposal_id" | "created_at" | "source_count" | "sources">;
    proposal = {
      proposal_id: proposalId,
      created_at: new Date().toISOString(),
      source_count: sourceRelPaths.length,
      sources: sourceRelPaths,
      ...parsed
    };
  } catch {
    proposal = fallbackProposal({
      proposalId,
      sources: sourceRelPaths,
      allowedTargets
    });
  }

  validateProposal(proposal);
  const written = await writeProposalArtifacts(proposal);
  console.log(`OK librarian proposal json: ${written.jsonPath}`);
  console.log(`OK librarian proposal md: ${written.mdPath}`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
