import fs from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";

export function compactTimestamp(date = new Date()): string {
  const iso = date.toISOString().replace(/[-:]/g, "");
  return iso.replace(/\.\d{3}Z$/, "Z");
}

export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "source";
}

export async function ensureDir(dirPath: string): Promise<void> {
  await fs.mkdir(dirPath, { recursive: true });
}

export async function readUtf8(filePath: string): Promise<string> {
  return fs.readFile(filePath, "utf8");
}

export async function writeUtf8(filePath: string, content: string): Promise<void> {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, content, "utf8");
}

export async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

export function wordCount(text: string): number {
  const words = text.trim().match(/\S+/g);
  return words ? words.length : 0;
}

export function stripCodeFences(text: string): string {
  return text.replace(/^```[a-zA-Z0-9_-]*\n?/u, "").replace(/\n?```$/u, "").trim();
}

export function looksLikeVideo(filePath: string): boolean {
  return [".mov", ".mp4", ".m4v", ".mkv", ".avi", ".webm", ".mpeg", ".mpg"].includes(
    path.extname(filePath).toLowerCase()
  );
}

export function htmlToText(html: string): string {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, "\"")
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

export async function runCommand(command: string, args: string[]): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const child = spawn(command, args, { stdio: "inherit" });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${command} exited with code ${code ?? "unknown"}`));
      }
    });
  });
}
