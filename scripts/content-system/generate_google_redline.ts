import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

type CliArgs = {
  month: string;
  ids?: string[];
};

type Op =
  | { type: "equal"; before: string; after: string }
  | { type: "delete"; before: string }
  | { type: "insert"; after: string };

function parseArgs(argv: string[]): CliArgs {
  let month = "2026-05";
  let idsRaw = "";

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]!;
    if (arg === "--month" && argv[i + 1]) {
      month = argv[++i]!;
      continue;
    }
    if (arg === "--ids" && argv[i + 1]) {
      idsRaw = argv[++i]!;
      continue;
    }
  }

  return {
    month,
    ids: idsRaw
      ? idsRaw
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean)
      : undefined,
  };
}

function stripGoogleExportHeader(text: string): string {
  if (!text.startsWith("# Google Doc tab export (plain text)")) {
    return text.trim();
  }
  const marker = "\n---\n";
  const idx = text.indexOf(marker);
  if (idx === -1) {
    return text.trim();
  }
  return text.slice(idx + marker.length).trim();
}

function stripMarkdownFrontmatter(text: string): string {
  if (!text.startsWith("---")) {
    return text;
  }
  const rest = text.slice(3);
  const end = rest.indexOf("\n---\n");
  if (end === -1) {
    return text;
  }
  return rest.slice(end + 5);
}

function markdownToPlain(text: string): string {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const output: string[] = [];

  for (const line of lines) {
    let next = line;

    // Remove heading markers.
    next = next.replace(/^#{1,6}\s+/, "");
    // Remove blockquote marker.
    next = next.replace(/^>\s?/, "");
    // Remove list markers.
    next = next.replace(/^\s*[-*+]\s+/, "");
    next = next.replace(/^\s*\d+\.\s+/, "");
    // Remove markdown links, keep visible text.
    next = next.replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1");
    // Remove simple emphasis markers.
    next = next.replace(/\*\*([^*]+)\*\*/g, "$1");
    next = next.replace(/\*([^*]+)\*/g, "$1");
    next = next.replace(/`([^`]+)`/g, "$1");

    output.push(next);
  }

  return output.join("\n");
}

function normalizeForCompare(text: string): string {
  return text
    .replace(/\r\n/g, "\n")
    .replace(/[“”]/g, "\"")
    .replace(/[‘’]/g, "'")
    .replace(/[—–]/g, "-")
    .replace(/…/g, "...")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function toBlocks(text: string): string[] {
  const byParagraph = text
    .replace(/\r\n/g, "\n")
    .split(/\n\s*\n/g)
    .map((b) => b.trim())
    .filter(Boolean);

  if (byParagraph.length >= 10) {
    return byParagraph;
  }

  return text
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function diffBlocks(beforeBlocks: string[], afterBlocks: string[]): Op[] {
  const aNorm = beforeBlocks.map(normalizeForCompare);
  const bNorm = afterBlocks.map(normalizeForCompare);
  const n = aNorm.length;
  const m = bNorm.length;

  const dp: number[][] = Array.from({ length: n + 1 }, () =>
    Array<number>(m + 1).fill(0),
  );

  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      if (aNorm[i] === bNorm[j]) {
        dp[i]![j] = dp[i + 1]![j + 1]! + 1;
      } else {
        dp[i]![j] = Math.max(dp[i + 1]![j]!, dp[i]![j + 1]!);
      }
    }
  }

  const ops: Op[] = [];
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (aNorm[i] === bNorm[j]) {
      ops.push({ type: "equal", before: beforeBlocks[i]!, after: afterBlocks[j]! });
      i++;
      j++;
      continue;
    }
    if (dp[i + 1]![j]! >= dp[i]![j + 1]!) {
      ops.push({ type: "delete", before: beforeBlocks[i]! });
      i++;
    } else {
      ops.push({ type: "insert", after: afterBlocks[j]! });
      j++;
    }
  }
  while (i < n) {
    ops.push({ type: "delete", before: beforeBlocks[i]! });
    i++;
  }
  while (j < m) {
    ops.push({ type: "insert", after: afterBlocks[j]! });
    j++;
  }
  return ops;
}

function strikeBlock(block: string): string {
  return block
    .split("\n")
    .map((line) => (line.trim() ? `~~${line}~~` : line))
    .join("\n");
}

function renderRedline(id: string, ops: Op[]): string {
  const out: string[] = [];
  out.push(`# ${id} — Full redline document`);
  out.push("");
  out.push(
    "Unchanged copy appears once. Changed areas show old text struck through, then updated text.",
  );
  out.push("");
  out.push("---");
  out.push("");

  let cursor = 0;
  while (cursor < ops.length) {
    const op = ops[cursor]!;
    if (op.type === "equal") {
      out.push(op.after);
      out.push("");
      cursor++;
      continue;
    }

    const deleted: string[] = [];
    const inserted: string[] = [];
    while (cursor < ops.length && ops[cursor]!.type !== "equal") {
      const branch = ops[cursor]!;
      if (branch.type === "delete") {
        deleted.push(branch.before);
      } else {
        inserted.push(branch.after);
      }
      cursor++;
    }

    if (deleted.length > 0) {
      for (const block of deleted) {
        out.push(strikeBlock(block));
        out.push("");
      }
    }
    if (inserted.length > 0) {
      for (const block of inserted) {
        out.push(block);
        out.push("");
      }
    }
  }

  return out.join("\n").trim() + "\n";
}

function discoverIds(draftsDir: string): string[] {
  return readdirSync(draftsDir)
    .map((name) => {
      const match = name.match(/^(may26_\d{2})_draft\.md$/);
      return match?.[1] ?? null;
    })
    .filter((v): v is string => Boolean(v))
    .sort();
}

function main(): void {
  const { month, ids } = parseArgs(process.argv.slice(2));
  const root = process.cwd();
  const monthRoot = resolve(root, `workspace/content_pipeline/monthly/${month}`);
  const googleDir = resolve(monthRoot, "drafts/_google_sync");
  const draftsDir = resolve(monthRoot, "drafts");
  const reviewDir = resolve(monthRoot, "review");
  mkdirSync(reviewDir, { recursive: true });

  const targets = ids && ids.length > 0 ? ids : discoverIds(draftsDir);
  if (targets.length === 0) {
    throw new Error(`No may article ids found in ${draftsDir}`);
  }

  const generated: string[] = [];
  const skipped: string[] = [];

  for (const id of targets) {
    const beforePath = resolve(googleDir, `${id}_plain.txt`);
    const afterPath = resolve(draftsDir, `${id}_draft.md`);
    const outPath = resolve(reviewDir, `${id}_google_vs_repo_redline.md`);

    if (!existsSync(beforePath)) {
      skipped.push(`${id} (missing before: ${beforePath})`);
      continue;
    }
    if (!existsSync(afterPath)) {
      skipped.push(`${id} (missing after: ${afterPath})`);
      continue;
    }

    const beforeRaw = stripGoogleExportHeader(readFileSync(beforePath, "utf8"));
    const afterRaw = markdownToPlain(stripMarkdownFrontmatter(readFileSync(afterPath, "utf8")));

    const beforeBlocks = toBlocks(beforeRaw);
    const afterBlocks = toBlocks(afterRaw);
    const ops = diffBlocks(beforeBlocks, afterBlocks);
    const rendered = renderRedline(id, ops);

    writeFileSync(outPath, rendered, "utf8");
    generated.push(outPath);
  }

  if (generated.length > 0) {
    console.log("Generated redline files:");
    for (const file of generated) {
      console.log(`- ${file}`);
    }
  }
  if (skipped.length > 0) {
    console.log("");
    console.log("Skipped:");
    for (const reason of skipped) {
      console.log(`- ${reason}`);
    }
  }
}

main();
