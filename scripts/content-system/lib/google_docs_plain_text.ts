import type { docs_v1 } from "googleapis";

function readParagraph(p: docs_v1.Schema$Paragraph): string {
  let text = "";
  for (const el of p.elements ?? []) {
    if (el.textRun?.content) text += el.textRun.content;
  }
  return text;
}

/** Concatenate visible text from structural elements (body, table cells, TOC). */
export function readStructuralElementsPlain(
  elements: docs_v1.Schema$StructuralElement[] | undefined,
): string {
  if (!elements?.length) return "";
  let text = "";
  for (const element of elements) {
    if (element.paragraph) {
      text += readParagraph(element.paragraph);
    } else if (element.table?.tableRows) {
      for (const row of element.table.tableRows) {
        for (const cell of row.tableCells ?? []) {
          text += readStructuralElementsPlain(cell.content);
        }
      }
    } else if (element.tableOfContents?.content) {
      text += readStructuralElementsPlain(element.tableOfContents.content);
    }
  }
  return text;
}

function collectTabTitles(tabs: docs_v1.Schema$Tab[] | undefined, acc: string[]): void {
  if (!tabs?.length) return;
  for (const t of tabs) {
    const title = t.tabProperties?.title?.trim();
    if (title) acc.push(title);
    collectTabTitles(t.childTabs, acc);
  }
}

/** Case-insensitive substring match on tab title (root or nested tabs). */
export function findTabByTitleSubstring(
  tabs: docs_v1.Schema$Tab[] | undefined,
  needle: string,
): docs_v1.Schema$Tab | null {
  const n = needle.trim().toLowerCase();
  if (!n) return null;
  if (!tabs?.length) return null;
  for (const t of tabs) {
    const title = (t.tabProperties?.title ?? "").toLowerCase();
    if (title.includes(n)) return t;
    const inner = findTabByTitleSubstring(t.childTabs, needle);
    if (inner) return inner;
  }
  return null;
}

export function listAllTabTitles(doc: docs_v1.Schema$Document): string[] {
  const acc: string[] = [];
  collectTabTitles(doc.tabs, acc);
  return acc;
}

/** Main body only (legacy first tab when `tabs` absent). */
export function plainTextFromDocumentBody(doc: docs_v1.Schema$Document): string {
  return readStructuralElementsPlain(doc.body?.content);
}

/** Plain text from a tab’s document body (multi-tab strategy docs). */
export function plainTextFromDocumentTab(
  tab: docs_v1.Schema$Tab,
): string {
  return readStructuralElementsPlain(tab.documentTab?.body?.content);
}
