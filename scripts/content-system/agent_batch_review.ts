#!/usr/bin/env tsx
/**
 * Multi-agent review for monthly article batches.
 * Cross-references new drafts against approved prior articles via OpenAI,
 * then runs SEO Monitor Gate, Librarian, and Chief Editor verdicts.
 *
 * Usage:
 *   npm run agent:batch-review -- --month 2026-06
 *   npm run agent:batch-review -- --month 2026-06 --article jun26_02
 *
 * Model: OPENAI_MODEL → OPENAI_NOTES_MODEL → gpt-5.5 (see env.example)
 */

import fs from "node:fs/promises";
import path from "node:path";

import { generateMarkdownFromPrompt } from "./lib/openai.js";
import { getOptionalEnv } from "./lib/env.js";
import { contentPipelineRoot, repoRoot } from "./lib/paths.js";

type ArticleSpec = {
  articleId: string;
  draftFile: string;
  briefFile: string;
  googleTab: string;
};

const BLACKLIST = [
  "security camera",
  "driveway camera",
  "property security",
  "perimeter security",
  "surveillance",
  "off-grid security",
  "hunting camera",
  "theft",
  "burglary",
  "deliveries"
];

/** Hard-fail vague or internal phrasing in client-facing drafts (May 2026 editorial standard). */
const VAGUE_PHRASES: { pattern: RegExp; label: string }[] = [
  { pattern: /\bactive sign\b/i, label: "active sign" },
  { pattern: /\breal sign\b/i, label: "real sign" },
  { pattern: /\bold sign\b/i, label: "old sign" },
  { pattern: /\bactive zone\b/i, label: "active zone" },
  { pattern: /\bequip the first active zone\b/i, label: "equip the first active zone" },
  { pattern: /\brelease the gate\b/i, label: "release the gate" },
  { pattern: /\bwalk sign\b/i, label: "Walk sign" },
  { pattern: /\bsign refreshes\b/i, label: "sign refreshes" },
  { pattern: /\barticle\s+\d+\b/i, label: "Article N" },
  { pattern: /\bthis batch\b/i, label: "this batch" },
  { pattern: /\bmay posts?\b/i, label: "May posts" },
  { pattern: /\bmay article\b/i, label: "May article" },
  { pattern: /\bpublished in may\b/i, label: "published in May" },
  { pattern: /\bstate trapping context\b/i, label: "state trapping context" },
  { pattern: /\btrap infrastructure\b/i, label: "trap infrastructure" },
  { pattern: /\bspend on gear\b/i, label: "spend on gear" },
  { pattern: /\bthis guide is only about\b/i, label: "this guide is only about" },
  { pattern: /\bthis article is about\b/i, label: "this article is about" },
  { pattern: /\bthis article explains\b/i, label: "this article explains" },
  { pattern: /\breaders searching\b/i, label: "Readers searching" }
];

const DEFAULT_REVIEW_MODEL = "gpt-5.5";

const JUNE_ARTICLES: ArticleSpec[] = [
  {
    articleId: "jun26_02",
    draftFile: "google_doc/Article_01_trapping_wild_hogs_texas.md",
    briefFile: "briefs/jun26_02_brief.md",
    googleTab: "Article 1"
  },
  {
    articleId: "jun26_01",
    draftFile: "google_doc/Article_02_hog_trap_placement.md",
    briefFile: "briefs/jun26_01_brief.md",
    googleTab: "Article 2"
  },
  {
    articleId: "jun26_05",
    draftFile: "google_doc/Article_03_electronic_hog_traps.md",
    briefFile: "briefs/jun26_05_brief.md",
    googleTab: "Article 3"
  },
  {
    articleId: "jun26_03",
    draftFile: "google_doc/Article_04_multi_trap_operation.md",
    briefFile: "briefs/jun26_03_brief.md",
    googleTab: "Article 4"
  },
  {
    articleId: "jun26_04",
    draftFile: "google_doc/Article_05_wild_hog_damage_field_guide.md",
    briefFile: "briefs/jun26_04_brief.md",
    googleTab: "Article 5"
  }
];

const APPROVED_REFERENCE_GLOBS = [
  "monthly/2026-05/review/may26_01_final_for_schell.md",
  "monthly/2026-05/review/may26_03_final_for_schell.md",
  "monthly/2026-05/review/may26_04_final_for_schell.md",
  "monthly/2026-05/review/may26_05_final_for_schell.md",
  "monthly/2026-05/drafts/may26_02_draft.md"
];

function parseArgs(argv: string[]): { month: string; article?: string } {
  let month = "";
  let article: string | undefined;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--month" && argv[i + 1]) {
      month = argv[++i];
    } else if (argv[i] === "--article" && argv[i + 1]) {
      article = argv[++i];
    }
  }
  if (!month) {
    throw new Error("Missing --month YYYY-MM");
  }
  return { month, article };
}

function truncate(text: string, max: number): string {
  if (text.length <= max) {
    return text;
  }
  return `${text.slice(0, max)}\n\n[... truncated for token budget ...]`;
}

async function readRepoFile(relPath: string): Promise<string> {
  const full = path.join(repoRoot, relPath.replace(/^\//, ""));
  return fs.readFile(full, "utf8");
}

async function loadApprovedCorpus(): Promise<string> {
  const chunks: string[] = [];
  for (const rel of APPROVED_REFERENCE_GLOBS) {
    const full = path.join(contentPipelineRoot, rel);
    try {
      const body = await fs.readFile(full, "utf8");
      chunks.push(`### Reference: ${rel}\n\n${truncate(body, 4500)}`);
    } catch {
      // skip missing
    }
  }
  return chunks.join("\n\n---\n\n");
}

type DeterministicResult = {
  emDashCount: number;
  emDashLines: string[];
  blacklistHits: { term: string; line: string }[];
  vagueHits: { label: string; line: string }[];
};

function runDeterministicChecks(draft: string): DeterministicResult {
  const lines = draft.split("\n");
  const emDashLines: string[] = [];
  lines.forEach((line, idx) => {
    if (line.includes("\u2014")) {
      emDashLines.push(`L${idx + 1}: ${line.trim()}`);
    }
  });
  const blacklistHits: { term: string; line: string }[] = [];
  const lower = draft.toLowerCase();
  for (const term of BLACKLIST) {
    if (lower.includes(term)) {
      const hitLine = lines.find((l) => l.toLowerCase().includes(term)) || "";
      blacklistHits.push({ term, line: hitLine.trim() });
    }
  }
  const vagueHits: { label: string; line: string }[] = [];
  for (const { pattern, label } of VAGUE_PHRASES) {
    const hitLine = lines.find((l) => pattern.test(l));
    if (hitLine) {
      vagueHits.push({ label, line: hitLine.trim() });
    }
  }
  return {
    emDashCount: emDashLines.length,
    emDashLines,
    blacklistHits,
    vagueHits
  };
}

function buildSystemPrompt(): string {
  return `You are running three HogEye content agent roles in one review pass:
1. SEO Monitor (Gate Mode) — per docs/agents/AGENT_SEO_MONITOR.md
2. Librarian — voice, registry continuity, internal links vs approved corpus
3. Chief Editor — final editorial verdict per docs/agents/AGENT_CHIEF_EDITOR.md

Be strict. Quote draft text for failures. Compare new draft to APPROVED REFERENCE ARTICLES for voice, structure, and vocabulary (sounder, conditioning, operator, trap site, closure).

Hard fails: em dash (—), blacklisted terms, vague field language (active sign, active zone, release the gate, Article N / May batch labels), robotic scope-declaration intros ("This guide is only about", "This article is about", "Readers searching", "This article explains"), North Star miss on H2 sections, missing FAQ or CTA, cannibalization vs May 2026 published topics.

Intro voice: openings must read like an operator speaking, not an SEO brief. Flag stiff meta sentences that announce scope instead of stating the problem.

Editorial taste is a gate, not optional polish. Facts and SEO compliance are only
the floor. Fail copy that is mechanical, bureaucratic, repetitive, overqualified,
keyword-led, or assembled from research notes. Check opening pull, sentence
integrity, paragraph flow, voice consistency, specificity, information pacing,
skimmability, practical usefulness, reader momentum, and the close. Quote every
failing passage and explain the cost to a landowner reading it.

Do not approve a draft solely because it has short sentences, a passing Flesch
score, transition words, correct facts, or complete headings.

Output markdown only, using this exact structure:

## Alignment vs Approved Corpus
**Status:** ALIGNED | MOSTLY ALIGNED | MISALIGNED
[Notes: voice, vocabulary, structure deltas vs May approved posts]

## SEO Monitor Gate Report
**Overall:** PASS | CONDITIONAL PASS | FAIL
[Checks 1-7 with PASS/FAIL bullets]

## Librarian Blessing
**Status:** BLESSED | BLESSED WITH FIXES | NOT BLESSED
[Registry/link/topic continuity notes]

## Chief Editor Verdict
**Status:** APPROVED | APPROVED WITH REQUIRED FIXES | NEEDS REVISION | BLOCKED
**Required fixes before Google Doc:**
1. ...
**Optional polish:**
- ...
**Notes for Schell:**

## Combined readiness for Google Doc
**GO / NO-GO:** GO only if SEO overall is PASS or CONDITIONAL PASS, Librarian not NOT BLESSED, Chief Editor not BLOCKED/NEEDS REVISION.`;
}

async function reviewArticle(params: {
  spec: ArticleSpec;
  monthRoot: string;
  approvedCorpus: string;
  doctrineBundle: string;
}): Promise<string> {
  const draftPath = path.join(params.monthRoot, params.spec.draftFile);
  const briefPath = path.join(params.monthRoot, params.spec.briefFile);
  const draft = await fs.readFile(draftPath, "utf8");
  const brief = await fs.readFile(briefPath, "utf8");
  const deterministic = runDeterministicChecks(draft);

  const user = [
    `# Article under review`,
    `- article_id: ${params.spec.articleId}`,
    `- google_doc_tab: ${params.spec.googleTab}`,
    `- brief_file: ${params.spec.briefFile}`,
    ``,
    `## Deterministic pre-checks (already run in code)`,
    `- em_dash_count: ${deterministic.emDashCount}`,
    deterministic.emDashLines.length
      ? `- em_dash_lines:\n${deterministic.emDashLines.map((l) => `  - ${l}`).join("\n")}`
      : `- em_dash_lines: none`,
    deterministic.blacklistHits.length
      ? `- blacklist_hits:\n${deterministic.blacklistHits.map((h) => `  - "${h.term}" in: ${h.line}`).join("\n")}`
      : `- blacklist_hits: none`,
    deterministic.vagueHits.length
      ? `- vague_language_hits:\n${deterministic.vagueHits.map((h) => `  - "${h.label}" in: ${h.line}`).join("\n")}`
      : `- vague_language_hits: none`,
    ``,
    `## Doctrine / strategy context`,
    params.doctrineBundle,
    ``,
    `## Brief`,
    brief,
    ``,
    `## Approved reference corpus (May 2026 client-approved / published voice)`,
    params.approvedCorpus,
    ``,
    `## New draft to review`,
    draft
  ].join("\n");

  const model = getOptionalEnv("OPENAI_MODEL", getOptionalEnv("OPENAI_NOTES_MODEL", DEFAULT_REVIEW_MODEL));
  return generateMarkdownFromPrompt({
    system: buildSystemPrompt(),
    user,
    model,
    temperature: 0.2
  });
}

async function loadDoctrineBundle(): Promise<string> {
  const parts = await Promise.all([
    readRepoFile("workspace/NORTH_STAR_POSITIONING.md").catch(() => ""),
    readRepoFile("workspace/KEYWORD_BLACKLIST.md").catch(() => ""),
    readRepoFile("workspace/content_pipeline/HUMANIZER_STYLE_GUIDE.md").catch(() => ""),
    readRepoFile("workspace/HOGEYE_CONTENT_STYLE_GUIDE.md").catch(() => ""),
    readRepoFile("workspace/CLIENT_FEEDBACK_SCHELL_APR2026.md").catch(() => ""),
    readRepoFile("workspace/CONTENT_REGISTRY.md").catch(() => "")
  ]);
  return parts.map((p, i) => truncate(p, i === 5 ? 6000 : 2500)).join("\n\n---\n\n");
}

async function main(): Promise<void> {
  const { month, article } = parseArgs(process.argv.slice(2));
  const monthRoot = path.join(contentPipelineRoot, "monthly", month);
  const reviewDir = path.join(monthRoot, "review");
  await fs.mkdir(reviewDir, { recursive: true });

  let specs = JUNE_ARTICLES;
  if (month !== "2026-06") {
    throw new Error(`Article map only defined for 2026-06; got ${month}`);
  }
  if (article) {
    specs = specs.filter((s) => s.articleId === article);
    if (!specs.length) {
      throw new Error(`Unknown article id: ${article}`);
    }
  }

  const approvedCorpus = await loadApprovedCorpus();
  const doctrineBundle = await loadDoctrineBundle();
  const summaryLines: string[] = [
    `# Agent batch review — ${month}`,
    ``,
    `Generated: ${new Date().toISOString()}`,
    `Model: ${getOptionalEnv("OPENAI_MODEL", getOptionalEnv("OPENAI_NOTES_MODEL", DEFAULT_REVIEW_MODEL))}`,
    ``,
    `| Article | SEO | Librarian | Chief Editor | Google Doc |`,
    `| --- | --- | --- | --- | --- |`
  ];

  for (const spec of specs) {
    process.stderr.write(`Reviewing ${spec.articleId} (${spec.googleTab})...\n`);
    const report = await reviewArticle({
      spec,
      monthRoot,
      approvedCorpus,
      doctrineBundle
    });
    const outPath = path.join(reviewDir, `${spec.articleId}_agent_review.md`);
    const header = [
      `# Agent review — ${spec.articleId}`,
      ``,
      `- Google Doc tab: **${spec.googleTab}**`,
      `- Draft: \`${spec.draftFile}\``,
      `- Brief: \`${spec.briefFile}\``,
      `- Generated: ${new Date().toISOString()}`,
      ``,
      `---`,
      ``
    ].join("\n");
    await fs.writeFile(outPath, header + report, "utf8");

    const seo = /SEO Monitor Gate Report[\s\S]*?\*\*Overall:\*\*\s*(PASS|CONDITIONAL PASS|FAIL)/i.exec(report);
    const lib = /Librarian Blessing[\s\S]*?\*\*Status:\*\*\s*(BLESSED WITH FIXES|BLESSED|NOT BLESSED)/i.exec(report);
    const ce = /Chief Editor Verdict[\s\S]*?\*\*Status:\*\*\s*(APPROVED WITH REQUIRED FIXES|APPROVED|NEEDS REVISION|BLOCKED)/i.exec(report);
    const go = /Combined readiness[\s\S]*?\*\*GO \/ NO-GO:\*\*\s*(GO|NO-GO)/i.exec(report);
    summaryLines.push(
      `| ${spec.googleTab} (\`${spec.articleId}\`) | ${seo?.[1] ?? "?"} | ${lib?.[1] ?? "?"} | ${ce?.[1] ?? "?"} | ${go?.[1] ?? "?"} |`
    );
  }

  summaryLines.push("", `Detail reports: \`monthly/${month}/review/jun26_*_agent_review.md\``);
  await fs.writeFile(path.join(reviewDir, "BATCH_AGENT_SUMMARY.md"), summaryLines.join("\n"), "utf8");
  console.log(`Wrote ${specs.length} review(s) to ${path.relative(repoRoot, reviewDir)}/`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
