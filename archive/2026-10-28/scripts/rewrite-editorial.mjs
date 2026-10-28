#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const OPENAI_URL = "https://api.openai.com/v1/chat/completions";
const DEFAULT_MODEL = "gpt-5.5";

function parseArgs(argv) {
  const options = { baseline: null, example: null, format: null, files: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--baseline") options.baseline = argv[++i];
    else if (arg === "--example") options.example = argv[++i];
    else if (arg === "--format") options.format = argv[++i];
    else if (arg.startsWith("--")) throw new Error(`Unknown flag: ${arg}`);
    else options.files.push(arg);
  }
  if (!options.baseline || !options.example) {
    throw new Error("--baseline and --example are required");
  }
  if (!["html", "markdown"].includes(options.format)) {
    throw new Error("--format must be html or markdown");
  }
  if (options.files.length === 0) throw new Error("Pass at least one JSON article");
  return options;
}

function stringValue(...values) {
  return values.find((value) => typeof value === "string" && value.trim())?.trim() ?? "";
}

function resolveArticle(raw, file) {
  const nested = raw.brief ?? raw.post ?? raw.data ?? {};
  const content = raw.content ?? nested.content ?? {};
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
  const title = stringValue(raw.title, content.title, nested.title);
  const keyword = stringValue(
    raw.focus_keyword,
    raw.targetKeyword,
    raw.target_keyword,
    content.focus_keyword,
    nested.target_keyword,
  );
  const externalId = stringValue(
    raw.externalId,
    raw.external_id,
    nested.externalId,
    nested.external_id,
    nested.brief_id,
    path.basename(file),
  );
  const targetWords = Number(
    raw.targetWordCount ??
      raw.target_word_count ??
      content.word_count ??
      nested.word_count ??
      800,
  );
  if (!title || !body) throw new Error(`${file}: cannot resolve title/body`);
  return { externalId, title, keyword, targetWords, body };
}

function setBody(raw, body) {
  if (typeof raw.content === "string") {
    raw.content = body;
    return;
  }
  if (raw.content && typeof raw.content === "object") {
    if ("html_content" in raw.content) raw.content.html_content = body;
    else if ("html" in raw.content) raw.content.html = body;
    else if ("markdown" in raw.content) raw.content.markdown = body;
    else if ("md" in raw.content) raw.content.md = body;
    else raw.content.html_content = body;
    raw.content.word_count = countWords(body);
    return;
  }
  if ("bodyMd" in raw) raw.bodyMd = body;
  else if ("html_content" in raw) raw.html_content = body;
  else raw.content = body;
}

function plainText(value) {
  return value
    .replace(/!\[[^\]]*]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)]\([^)]*\)/g, "$1")
    .replace(/<[^>]+>/g, " ")
    .replace(/[`*_>#|~-]/g, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function countWords(value) {
  return plainText(value).match(/\b[\w’'-]+\b/g)?.length ?? 0;
}

function hasTldr(body, format) {
  if (format === "html") {
    return /^\s*<p[^>]*>\s*<strong[^>]*>\s*TL;DR:\s*<\/strong>/i.test(body);
  }
  return /^\s*>\s*\*\*TL;DR:\*\*/i.test(body);
}

function extractTldr(body, format) {
  const pattern =
    format === "html"
      ? /^\s*(<p[^>]*>\s*<strong[^>]*>\s*TL;DR:\s*<\/strong>.*?<\/p>)/is
      : /^\s*(>\s*\*\*TL;DR:\*\*.*?)(?:\n\s*\n|$)/is;
  return body.match(pattern)?.[1]?.trim() ?? "";
}

async function rewrite({ apiKey, model, baseline, example, format, article }) {
  const minimum = Math.ceil(article.targetWords * 0.95);
  const maximum = Math.floor(article.targetWords * 1.05);
  const tldrPattern =
    format === "html"
      ? "<p><strong>TL;DR:</strong> 35-60 words...</p>"
      : "> **TL;DR:** 35-60 words...";

  const system = `You are a senior brand editor, not an SEO text generator.
Facts are the floor. Rewrite for style, taste, clarity, flow, practical usefulness,
reader momentum, and enjoyment. Preserve the brand baseline and all supported facts.
Never invent facts, prices, dates, product claims, stories, or citations.
Return JSON only with one key: body.`;

  const user = `BRAND BASELINE:
${baseline.slice(0, 20000)}

APPROVED WRITING EXAMPLE:
${example.body.slice(0, 16000)}

ARTICLE TO REWRITE:
Title: ${article.title}
Target keyword: ${article.keyword}
Required body words: ${minimum}-${maximum}
Output format: ${format}

${article.body}

REQUIREMENTS:
- Keep the title, topic, intent, product facts, dates, prices, citations, and URLs.
- Do not copy phrases from the approved example; match its judgment, pace, clarity, and taste.
- Begin the body with exactly this kind of first block: ${tldrPattern}
- The TL;DR must answer intent and give the practical takeaway without adding a new fact.
- Give each paragraph one job. Use concrete language and varied sentence rhythm.
- Compress research dumps, repeated caveats, repeated conclusions, and generic transitions.
- Preserve useful headings, lists, links, and FAQs, but reorder or tighten them for flow.
- Do not mention SEO, keywords, drafting, revisions, prompts, articles, pages, or word counts.
- Stay inside ${minimum}-${maximum} body words, including the TL;DR.`;

  const requestBody = {
    model,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: system },
      { role: "user", content: user },
    ],
  };
  if (!/^gpt-5\.5/i.test(model)) requestBody.temperature = 0.35;

  const response = await fetch(OPENAI_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
    signal: AbortSignal.timeout(120_000),
  });
  if (!response.ok) {
    throw new Error(`OpenAI ${response.status}: ${(await response.text()).slice(0, 500)}`);
  }
  const json = await response.json();
  const text = json.choices?.[0]?.message?.content;
  if (typeof text !== "string" || !text.trim()) throw new Error("OpenAI returned no content");
  const parsed = JSON.parse(text);
  if (typeof parsed.body !== "string" || !parsed.body.trim()) {
    throw new Error("OpenAI response is missing body");
  }
  return parsed.body.trim();
}

async function resizeBody({ apiKey, model, format, body, minimum, maximum }) {
  const tldr = extractTldr(body, format);
  const requestBody = {
    model,
    response_format: { type: "json_object" },
    messages: [
      {
        role: "system",
        content:
          "You are a ruthless line editor. Preserve facts, URLs, useful structure, " +
          "format, and the first TL;DR, but hit the required word range exactly. " +
          "Remove repetition, caveats, filler, and low-value detail before useful substance. " +
          "Return JSON only with one key: body.",
      },
      {
        role: "user",
        content: `Current body words: ${countWords(body)}
Required body words: ${minimum}-${maximum}
Format: ${format}

Rewrite this body to land inside the required range. Do not add facts or URLs.

${body}`,
      },
    ],
  };
  if (!/^gpt-5\.5/i.test(model)) requestBody.temperature = 0.2;
  const response = await fetch(OPENAI_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
    signal: AbortSignal.timeout(120_000),
  });
  if (!response.ok) {
    throw new Error(`OpenAI ${response.status}: ${(await response.text()).slice(0, 500)}`);
  }
  const json = await response.json();
  const text = json.choices?.[0]?.message?.content;
  if (typeof text !== "string" || !text.trim()) throw new Error("OpenAI returned no content");
  const parsed = JSON.parse(text);
  if (typeof parsed.body !== "string" || !parsed.body.trim()) {
    throw new Error("OpenAI resize response is missing body");
  }
  let resized = parsed.body.trim();
  if (tldr && !hasTldr(resized, format)) {
    resized = `${tldr}\n\n${resized}`;
  }
  return resized;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY is required");
  const model = process.env.OPENAI_MODEL || DEFAULT_MODEL;
  const baseline = await readFile(options.baseline, "utf8");
  const exampleRaw = JSON.parse(await readFile(options.example, "utf8"));
  const example = resolveArticle(exampleRaw, options.example);

  for (const file of options.files) {
    const raw = JSON.parse(await readFile(file, "utf8"));
    const article = resolveArticle(raw, file);
    const minimum = Math.ceil(article.targetWords * 0.95);
    const maximum = Math.floor(article.targetWords * 1.05);
    let body = await rewrite({
      apiKey,
      model,
      baseline,
      example,
      format: options.format,
      article,
    });
    let words = countWords(body);
    for (let attempt = 1; attempt <= 5 && (words < minimum || words > maximum); attempt += 1) {
      words = countWords(body);
      console.warn(
        `! ${article.externalId}: resize attempt ${attempt} starts at ${words} words; ` +
          `retrying for ${minimum}-${maximum}`,
      );
      body = await resizeBody({
        apiKey,
        model,
        format: options.format,
        body,
        minimum,
        maximum,
      });
      words = countWords(body);
    }
    if (!hasTldr(body, options.format)) throw new Error(`${file}: missing first-block TL;DR`);
    if (words < minimum || words > maximum) {
      throw new Error(`${file}: ${words} words outside ${minimum}-${maximum}`);
    }
    setBody(raw, body);
    await writeFile(file, `${JSON.stringify(raw, null, 2)}\n`, "utf8");
    console.log(`✓ ${article.externalId}: ${words} words`);
  }
}

main().catch((error) => {
  console.error(`✗ ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
