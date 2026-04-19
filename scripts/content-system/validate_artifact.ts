import path from "node:path";

import matter from "gray-matter";

import { readUtf8 } from "./lib/runtime.js";

type Stage =
  | "brief"
  | "research_pack"
  | "draft"
  | "qa"
  | "handoff"
  | "processed_transcript"
  | "derived_note"
  | "unknown";

type ValidationResult = {
  path: string;
  stage: Stage;
  issues: string[];
  warnings: string[];
};

const BANNED_TERMS = [
  "ranchers",
  "property security",
  "perimeter security",
  "general monitoring",
  "surveillance",
  "land security"
];

function detectStage(filePath: string): Stage {
  const normalized = filePath.replaceAll(path.sep, "/");
  if (normalized.endsWith("_brief.md")) return "brief";
  if (normalized.endsWith("_research_pack.md")) return "research_pack";
  if (normalized.endsWith("_draft.md")) return "draft";
  if (normalized.endsWith("_qa.md")) return "qa";
  if (normalized.endsWith("_handoff.md")) return "handoff";
  if (normalized.includes("/sources/transcripts/processed/")) return "processed_transcript";
  if (normalized.includes("/sources/derived_notes/")) return "derived_note";
  return "unknown";
}

function requireHeading(body: string, issues: string[], heading: string): void {
  if (!body.includes(heading)) {
    issues.push(`Missing required heading: ${heading}`);
  }
}

function requireLineValue(body: string, issues: string[], label: string): void {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`^- ${escaped}:\\s*(.+)$`, "m");
  const match = body.match(regex);
  if (!match || !match[1].trim() || match[1].trim().startsWith("[")) {
    issues.push(`Missing or placeholder value for: ${label}`);
  }
}

function checkBannedTerms(body: string, issues: string[]): void {
  const safeContextHints = [
    "do-not-say",
    "banned",
    "rejected adjacent framing",
    "does not use banned term",
    "no drift into",
    "not allowed",
    "specific claims not allowed",
    "key constraints extracted",
    "generic security/surveillance language"
  ];

  let skipFollowingBullets = 0;
  for (const line of body.split("\n")) {
    const lowerLine = line.toLowerCase();
    if (safeContextHints.some((hint) => lowerLine.includes(hint))) {
      skipFollowingBullets = 3;
      continue;
    }
    if (skipFollowingBullets > 0 && lowerLine.trimStart().startsWith("-")) {
      skipFollowingBullets -= 1;
      continue;
    }
    for (const term of BANNED_TERMS) {
      if (lowerLine.includes(term.toLowerCase())) {
        issues.push(`Contains banned term or framing in content: ${term}`);
      }
    }
  }
}

function checkTemplatePlaceholders(body: string, warnings: string[]): void {
  const placeholders = ["[Replace with final H1]", "[Section]", "[Question]", "PASS or FAIL"];
  for (const token of placeholders) {
    if (body.includes(token)) {
      warnings.push(`Contains template placeholder: ${token}`);
    }
  }
}

function validateBrief(body: string, result: ValidationResult): void {
  [
    "## Article identity",
    "## SEO target",
    "## Audience and positioning",
    "## Data inputs used",
    "## Source notes",
    "## Approval gate"
  ].forEach((heading) => requireHeading(body, result.issues, heading));
  requireLineValue(body, result.issues, "primary_keyword");
  requireLineValue(body, result.issues, "approved audience wording");
  requireLineValue(body, result.issues, "approved product framing");
  requireLineValue(body, result.issues, "dataforseo sources");
}

function validateResearchPack(body: string, result: ValidationResult): void {
  [
    "## Approved positioning lock",
    "## Website-derived truth",
    "## DataForSEO findings (required)",
    "## Excluded unsupported claims",
    "## Writing constraints for draft"
  ].forEach((heading) => requireHeading(body, result.issues, heading));
  requireLineValue(body, result.issues, "canonical framing used");
  requireLineValue(body, result.issues, "dataset file path(s)");
}

function validateDraft(body: string, result: ValidationResult): void {
  ["## Metadata", "## Claims audit notes"].forEach((heading) =>
    requireHeading(body, result.issues, heading)
  );
  requireLineValue(body, result.issues, "primary_keyword");
  requireLineValue(body, result.issues, "approved_positioning_angle");
  if (!body.includes("dataforseo:")) {
    result.issues.push("Draft metadata is missing dataforseo input reference.");
  }
}

function validateQA(body: string, result: ValidationResult): void {
  [
    "## Brand compliance checks",
    "## Factual compliance checks",
    "## SEO completeness checks",
    "## QA result"
  ].forEach((heading) => requireHeading(body, result.issues, heading));
  if (!body.includes("## Humanizer pass checks") && !body.includes("## Final pass checks")) {
    result.warnings.push("Missing Final pass checks (or legacy Humanizer pass checks) section.");
  }
  requireLineValue(body, result.issues, "status");
  requireLineValue(body, result.issues, "reviewed_by");
}

function validateProcessedTranscript(frontmatter: Record<string, unknown>, body: string, result: ValidationResult): void {
  ["source_media", "source_filename", "transcribed_at", "model", "raw_json", "raw_txt"].forEach((key) => {
    if (!frontmatter[key]) {
      result.issues.push(`Missing transcript frontmatter key: ${key}`);
    }
  });
  requireHeading(body, result.issues, "# Transcript");
}

function validateDerivedNote(frontmatter: Record<string, unknown>, body: string, result: ValidationResult): void {
  ["source_transcript", "derived_at", "model", "editorial_spec_version", "prompt_system"].forEach((key) => {
    if (!frontmatter[key]) {
      result.issues.push(`Missing derived-note frontmatter key: ${key}`);
    }
  });
  if (!body.trim()) {
    result.issues.push("Derived notes body is empty.");
  }
}

async function validateOne(filePath: string): Promise<ValidationResult> {
  const absolutePath = path.resolve(filePath);
  const raw = await readUtf8(absolutePath);
  const parsed = matter(raw);
  const stage = detectStage(absolutePath);
  const result: ValidationResult = {
    path: absolutePath,
    stage,
    issues: [],
    warnings: []
  };

  if (stage === "unknown") {
    result.warnings.push("Unknown stage; no stage-specific validation applied.");
  }

  checkBannedTerms(parsed.content, result.issues);
  checkTemplatePlaceholders(parsed.content, result.warnings);

  switch (stage) {
    case "brief":
      validateBrief(parsed.content, result);
      break;
    case "research_pack":
      validateResearchPack(parsed.content, result);
      break;
    case "draft":
      validateDraft(parsed.content, result);
      break;
    case "qa":
      validateQA(parsed.content, result);
      break;
    case "processed_transcript":
      validateProcessedTranscript(parsed.data, parsed.content, result);
      break;
    case "derived_note":
      validateDerivedNote(parsed.data, parsed.content, result);
      break;
    default:
      break;
  }

  return result;
}

async function main(): Promise<void> {
  const paths = process.argv.slice(2);
  if (paths.length === 0) {
    throw new Error("Usage: npm run validate-artifact -- <path> [more-paths]");
  }

  const results = await Promise.all(paths.map((filePath) => validateOne(filePath)));
  console.log(JSON.stringify(results, null, 2));

  const hasIssues = results.some((result) => result.issues.length > 0);
  if (hasIssues) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
