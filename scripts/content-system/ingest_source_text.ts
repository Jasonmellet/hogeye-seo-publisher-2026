import fs from "node:fs/promises";
import path from "node:path";

import { relativeToRepo, sourceRoots } from "./lib/paths.js";
import {
  compactTimestamp,
  ensureDir,
  htmlToText,
  readUtf8,
  slugify,
  wordCount,
  writeUtf8
} from "./lib/runtime.js";

function yamlLine(key: string, value: string | number | null): string {
  if (value === null) {
    return `${key}: null`;
  }
  if (typeof value === "number") {
    return `${key}: ${value}`;
  }
  return `${key}: ${JSON.stringify(value)}`;
}

function normalizeSourceText(filePath: string, text: string): string {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".html" || ext === ".htm") {
    return htmlToText(text);
  }
  return text.trim();
}

async function main(): Promise<void> {
  const inputArg = process.argv[2];
  if (!inputArg) {
    throw new Error("Usage: npm run ingest-source -- <file-path>");
  }

  const inputPath = path.resolve(inputArg);
  const stat = await fs.stat(inputPath);
  if (!stat.isFile()) {
    throw new Error(`Input path is not a file: ${inputPath}`);
  }

  const rawText = await readUtf8(inputPath);
  const sourceText = normalizeSourceText(inputPath, rawText);
  if (!sourceText) {
    throw new Error("Source file produced empty text after normalization.");
  }

  await ensureDir(sourceRoots.sourceNotes);
  const titleBase = path.basename(inputPath, path.extname(inputPath));
  const outputPath = path.join(
    sourceRoots.sourceNotes,
    `${compactTimestamp()}_${slugify(titleBase)}.md`
  );

  await writeUtf8(
    outputPath,
    [
      "---",
      yamlLine("title", `${titleBase} source note`),
      yamlLine("source_path", relativeToRepo(inputPath)),
      yamlLine("source_filename", path.basename(inputPath)),
      yamlLine("source_kind", "text"),
      yamlLine("ingested_at", new Date().toISOString()),
      yamlLine("original_format", path.extname(inputPath).toLowerCase() || "unknown"),
      yamlLine("word_count", wordCount(sourceText)),
      "---",
      "",
      "# Source Note",
      "",
      sourceText,
      ""
    ].join("\n")
  );

  console.log(`OK source note created: ${outputPath}`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
