#!/usr/bin/env node

import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const JEV_URL = "https://api.typesafe.ai/v1/systemone";
const JEV_MODEL = "jev-latest";
const TIMEOUT_MS = 30_000;
const MIN_EDITORIAL_SCORE = 1.3;
const MAX_CONCERN_NOUL = 0.45;

const QUESTIONS = {
  sentence_integrity: {
    type: "noul",
    instructions:
      "Does the article contain broken, fused, garbled, or grammatically incomplete sentences that make a reader stop and reconstruct the meaning?",
    criteria: {
      true: "At least one reader-facing sentence is malformed or requires reconstruction",
      false: "Every sentence is grammatically intact and immediately understandable",
    },
  },
  research_dump: {
    type: "noul",
    instructions:
      "Does the article read like research notes, a regulation dump, or a list of caveats rather than shaped reader-facing prose?",
    criteria: {
      true: "Facts, dates, qualifications, or warnings are piled up without useful pacing and hierarchy",
      false: "Research is selected, ordered, and explained around the reader's practical need",
    },
  },
  reader_effort: {
    type: "score",
    instructions:
      "How easy is this article to understand on the first read without backtracking?",
    criteria: [
      "Hard to follow: dense, awkward, or confusing enough to require rereading",
      "Understandable but uneven: some passages create avoidable effort",
      "Effortless: clear on the first read from opening through close",
    ],
  },
  flow_and_hierarchy: {
    type: "score",
    instructions:
      "How well does the article order and pace information around the reader's question?",
    criteria: [
      "Poorly shaped: paragraphs feel assembled, repetitive, or out of order",
      "Competent: the structure works but contains detours or overloaded sections",
      "Purposeful: each section earns its place and naturally leads to the next",
    ],
  },
  style_and_taste: {
    type: "score",
    instructions:
      "How much does this sound like a skilled human writer with judgment, voice, specificity, and varied rhythm rather than an SEO template?",
    criteria: [
      "Mechanical: generic, bureaucratic, keyword-led, repetitive, or visibly generated",
      "Competent but generic: accurate prose without much voice or editorial judgment",
      "Distinctive and natural: confident, concrete, brand-appropriate prose with taste",
    ],
  },
  reader_momentum: {
    type: "score",
    instructions:
      "How likely is the target reader to willingly continue from paragraph to paragraph?",
    criteria: [
      "Low momentum: the opening, repetition, or density makes stopping likely",
      "Mixed momentum: useful information but attention drops in places",
      "Strong momentum: useful, enjoyable, and consistently rewarding to read",
    ],
  },
};

function fail(message) {
  console.error(`[editorial-gate] ${message}`);
  process.exitCode = 1;
}

function parseArgs(argv) {
  const options = { baseline: null, report: null, inputs: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--baseline") options.baseline = argv[++i];
    else if (arg.startsWith("--baseline=")) options.baseline = arg.slice(11);
    else if (arg === "--report") options.report = argv[++i];
    else if (arg.startsWith("--report=")) options.report = arg.slice(9);
    else if (arg.startsWith("--")) throw new Error(`Unknown flag: ${arg}`);
    else options.inputs.push(arg);
  }
  if (!options.baseline) throw new Error("--baseline is required");
  if (options.inputs.length === 0) throw new Error("Pass at least one JSON file or directory");
  return options;
}

async function collectJsonFiles(inputs) {
  const files = [];
  async function visit(input) {
    const info = await stat(input);
    if (info.isDirectory()) {
      for (const name of await readdir(input)) await visit(path.join(input, name));
    } else if (input.endsWith(".json")) {
      files.push(input);
    }
  }
  for (const input of inputs) await visit(input);
  return files.sort();
}

function stringValue(...values) {
  return values.find((value) => typeof value === "string" && value.trim())?.trim() ?? "";
}

function articleFromJson(raw, file) {
  const nested = raw.brief ?? raw.post ?? raw.data ?? {};
  const content = raw.content ?? nested.content ?? {};
  const title = stringValue(
    raw.title,
    content.title,
    nested.title,
    raw.name,
  );
  const body = stringValue(
    typeof content === "string" ? content : null,
    content.html_content,
    content.html,
    content.markdown,
    content.md,
    raw.bodyMd,
    raw.html_content,
    raw.article,
    raw.body,
  );
  const externalId = stringValue(
    raw.externalId,
    raw.external_id,
    nested.externalId,
    nested.external_id,
    nested.brief_id,
    path.basename(file),
  );
  if (!title || !body) throw new Error(`${file}: cannot resolve title/body`);
  return { externalId, title, body };
}

async function askJev(apiKey, state, retry = true) {
  const response = await fetch(JEV_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model: JEV_MODEL, state, questions: QUESTIONS }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (response.ok) return (await response.json()).answers;
  if (retry && (response.status === 429 || response.status === 529)) {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return askJev(apiKey, state, false);
  }
  throw new Error(`Jev returned ${response.status}: ${(await response.text()).slice(0, 200)}`);
}

function evaluate(answers) {
  const failures = [];
  for (const id of ["sentence_integrity", "research_dump"]) {
    const answer = answers[id];
    if (!answer || answer.type !== "noul") throw new Error(`Missing noul answer: ${id}`);
    if (answer.noul >= MAX_CONCERN_NOUL) {
      failures.push(`${id} p=${answer.noul.toFixed(2)}`);
    }
  }
  for (const id of [
    "reader_effort",
    "flow_and_hierarchy",
    "style_and_taste",
    "reader_momentum",
  ]) {
    const answer = answers[id];
    if (!answer || answer.type !== "score") throw new Error(`Missing score answer: ${id}`);
    if (answer.score < MIN_EDITORIAL_SCORE) {
      failures.push(
        `${id} ${answer.score.toFixed(2)}/2 (confidence ${answer.confidence.toFixed(2)})`,
      );
    }
  }
  return failures;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const apiKey = process.env.TYPESAFE_API_KEY;
  if (!apiKey) throw new Error("TYPESAFE_API_KEY is required; editorial review fails closed");

  const baseline = await readFile(options.baseline, "utf8");
  if (!baseline.trim()) throw new Error("Brand baseline is empty");

  const files = await collectJsonFiles(options.inputs);
  if (files.length === 0) throw new Error("No JSON files found");

  const results = [];
  for (const file of files) {
    const raw = JSON.parse(await readFile(file, "utf8"));
    const article = articleFromJson(raw, file);
    const answers = await askJev(apiKey, {
      brand_baseline: baseline,
      editorial_standard:
        "Facts are the floor. Publishable copy must also be clear, shaped, natural, useful, enjoyable, and easy to read on the first pass.",
      article,
    });
    const failures = evaluate(answers);
    results.push({ file, externalId: article.externalId, pass: failures.length === 0, failures, answers });
    if (failures.length) {
      fail(`${article.externalId}: ${failures.join("; ")}`);
    } else {
      console.log(`[editorial-gate] ✓ ${article.externalId}`);
    }
  }

  if (options.report) {
    await writeFile(options.report, `${JSON.stringify({ results }, null, 2)}\n`, "utf8");
  }
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
