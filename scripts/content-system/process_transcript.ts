import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

import matter from "gray-matter";

import { getOptionalEnv } from "./lib/env.js";
import { generateMarkdownFromPrompt } from "./lib/openai.js";
import { doctrineRoots, relativeToRepo, sourceRoots } from "./lib/paths.js";
import {
  compactTimestamp,
  ensureDir,
  readUtf8,
  slugify,
  stripCodeFences,
  wordCount,
  writeUtf8
} from "./lib/runtime.js";

const DERIVED_NOTES_PROMPT_PATH = path.join(doctrineRoots.prompts, "workflow", "derive_notes.md");

function yamlLine(key: string, value: string | number | boolean | null): string {
  if (value === null) {
    return `${key}: null`;
  }
  if (typeof value === "boolean" || typeof value === "number") {
    return `${key}: ${value}`;
  }
  return `${key}: ${JSON.stringify(value)}`;
}

function buildUserPrompt(transcriptPath: string, frontmatter: Record<string, unknown>, content: string): string {
  const metadataLines = [
    `source_transcript_path: ${transcriptPath}`,
    `source_media: ${String(frontmatter.source_media || "")}`,
    `source_filename: ${String(frontmatter.source_filename || "")}`,
    `transcribed_at: ${String(frontmatter.transcribed_at || "")}`,
    `word_count: ${String(frontmatter.word_count || "")}`
  ].join("\n");

  return [
    "Use the transcript below to produce a reusable HogEye derived-notes document.",
    "Stay tied to the source text. Do not invent facts, metrics, examples, or claims.",
    "Prioritize distinctive field language, trap-operation insights, practical cautions, and reusable content angles.",
    "Call out anything that sounds useful but still needs website or internal-doc confirmation before publishing.",
    "",
    "Transcript metadata:",
    metadataLines,
    "",
    "Transcript text:",
    content.trim()
  ].join("\n");
}

export async function processTranscriptFile(processedTranscriptPath: string): Promise<string> {
  const absolutePath = path.resolve(processedTranscriptPath);
  const rawMarkdown = await readUtf8(absolutePath);
  const parsed = matter(rawMarkdown);

  const systemPrompt = await readUtf8(DERIVED_NOTES_PROMPT_PATH);
  const userPrompt = buildUserPrompt(absolutePath, parsed.data, parsed.content);
  const completion = await generateMarkdownFromPrompt({
    system: systemPrompt,
    user: userPrompt,
    model: getOptionalEnv("OPENAI_NOTES_MODEL", "gpt-5.4-mini"),
    temperature: 0.2
  });

  const cleanBody = stripCodeFences(completion);
  const timestamp = compactTimestamp();
  const titleSeed =
    String(parsed.data.title || parsed.data.source_filename || path.basename(absolutePath, path.extname(absolutePath)));
  const outputPath = path.join(sourceRoots.derivedNotes, `${timestamp}_${slugify(titleSeed)}.md`);

  await ensureDir(sourceRoots.derivedNotes);
  await writeUtf8(
    outputPath,
    [
      "---",
      yamlLine("title", `${titleSeed} derived notes`),
      yamlLine("source_transcript", relativeToRepo(absolutePath)),
      yamlLine("derived_at", new Date().toISOString()),
      yamlLine("model", getOptionalEnv("OPENAI_NOTES_MODEL", "gpt-5.4-mini")),
      yamlLine("editorial_spec_version", "hogeye-derived-notes-v1"),
      yamlLine("prompt_system", relativeToRepo(DERIVED_NOTES_PROMPT_PATH)),
      yamlLine("word_count", wordCount(cleanBody)),
      "---",
      "",
      cleanBody,
      ""
    ].join("\n")
  );

  return outputPath;
}

async function main(): Promise<void> {
  const transcriptArg = process.argv[2];
  if (!transcriptArg) {
    throw new Error("Usage: npm run process-transcript -- <processed-transcript.md>");
  }

  await fs.access(path.resolve(transcriptArg));
  const outputPath = await processTranscriptFile(transcriptArg);
  console.log(`OK derived notes created: ${outputPath}`);
}

const isDirectRun =
  typeof process.argv[1] === "string" &&
  import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;

if (isDirectRun) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
