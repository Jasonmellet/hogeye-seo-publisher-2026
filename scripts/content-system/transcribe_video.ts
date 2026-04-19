import fs from "node:fs/promises";
import path from "node:path";

import { processTranscriptFile } from "./process_transcript.js";
import { transcribeAudioFile } from "./lib/openai.js";
import { relativeToRepo, sourceRoots } from "./lib/paths.js";
import {
  compactTimestamp,
  ensureDir,
  looksLikeVideo,
  runCommand,
  slugify,
  wordCount,
  writeUtf8
} from "./lib/runtime.js";

const MAX_UPLOAD_BYTES = 25 * 1024 * 1024;

function yamlLine(key: string, value: string | number | boolean | null): string {
  if (value === null) {
    return `${key}: null`;
  }
  if (typeof value === "boolean" || typeof value === "number") {
    return `${key}: ${value}`;
  }
  return `${key}: ${JSON.stringify(value)}`;
}

async function maybeExtractAudio(mediaPath: string, outputBase: string): Promise<string | null> {
  const stat = await fs.stat(mediaPath);
  if (!looksLikeVideo(mediaPath) && stat.size <= MAX_UPLOAD_BYTES) {
    return null;
  }

  const extractedPath = path.join(sourceRoots.transcriptsRaw, `${outputBase}.mp3`);
  await runCommand("ffmpeg", [
    "-y",
    "-i",
    mediaPath,
    "-vn",
    "-acodec",
    "libmp3lame",
    "-ac",
    "1",
    "-ar",
    "16000",
    "-b:a",
    "64k",
    extractedPath
  ]);
  return extractedPath;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const auto = args.includes("--auto");
  const mediaArg = args.find((arg) => !arg.startsWith("--"));
  if (!mediaArg) {
    throw new Error("Usage: npm run transcribe -- [--auto] <media-path>");
  }

  const mediaPath = path.resolve(mediaArg);
  const stat = await fs.stat(mediaPath);
  if (!stat.isFile()) {
    throw new Error(`Input path is not a file: ${mediaPath}`);
  }

  await ensureDir(sourceRoots.transcriptsRaw);
  await ensureDir(sourceRoots.transcriptsProcessed);

  const timestamp = compactTimestamp();
  const slug = slugify(path.basename(mediaPath, path.extname(mediaPath)));
  const outputBase = `${timestamp}_${slug}`;

  const extractedAudioPath = await maybeExtractAudio(mediaPath, outputBase);
  const uploadPath = extractedAudioPath || mediaPath;
  const uploadStat = await fs.stat(uploadPath);
  if (uploadStat.size > MAX_UPLOAD_BYTES) {
    throw new Error(`Upload artifact exceeds 25 MB after preprocessing: ${uploadPath}`);
  }

  const verbose = await transcribeAudioFile(uploadPath);
  const transcriptText = String(verbose.text || "").trim();
  if (!transcriptText) {
    throw new Error("Transcription returned empty text.");
  }

  const rawJsonPath = path.join(sourceRoots.transcriptsRaw, `${outputBase}.verbose.json`);
  const rawTxtPath = path.join(sourceRoots.transcriptsRaw, `${outputBase}.txt`);
  const processedPath = path.join(sourceRoots.transcriptsProcessed, `${outputBase}.md`);

  await fs.writeFile(rawJsonPath, JSON.stringify(verbose, null, 2), "utf8");
  await fs.writeFile(rawTxtPath, `${transcriptText}\n`, "utf8");

  const duration = typeof verbose.duration === "number" ? verbose.duration : null;
  const language = typeof verbose.language === "string" ? verbose.language : null;
  const processedMarkdown = [
    "---",
    yamlLine("title", `${path.basename(mediaPath, path.extname(mediaPath))} transcript`),
    yamlLine("source_media", relativeToRepo(mediaPath)),
    yamlLine("source_filename", path.basename(mediaPath)),
    yamlLine("extracted_audio", extractedAudioPath ? relativeToRepo(extractedAudioPath) : null),
    yamlLine("transcribed_at", new Date().toISOString()),
    yamlLine("model", "whisper-1"),
    yamlLine("api", "openai/audio/transcriptions"),
    yamlLine("language", language),
    yamlLine("duration_seconds", duration),
    yamlLine("word_count", wordCount(transcriptText)),
    yamlLine("raw_json", relativeToRepo(rawJsonPath)),
    yamlLine("raw_txt", relativeToRepo(rawTxtPath)),
    "---",
    "",
    "# Transcript",
    "",
    transcriptText,
    ""
  ].join("\n");

  await writeUtf8(processedPath, processedMarkdown);
  console.log(`OK transcript created: ${processedPath}`);

  if (auto) {
    const derivedPath = await processTranscriptFile(processedPath);
    console.log(`OK derived notes created: ${derivedPath}`);
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
