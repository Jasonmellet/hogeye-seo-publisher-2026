import path from "node:path";
import dotenv from "dotenv";

import { repoRoot } from "./paths.js";

let loaded = false;

export function loadRepoEnv(): void {
  if (loaded) {
    return;
  }
  dotenv.config({ path: path.join(repoRoot, ".env") });
  loaded = true;
}

export function getRequiredEnv(name: string): string {
  loadRepoEnv();
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function getOptionalEnv(name: string, fallback = ""): string {
  loadRepoEnv();
  return process.env[name]?.trim() || fallback;
}
