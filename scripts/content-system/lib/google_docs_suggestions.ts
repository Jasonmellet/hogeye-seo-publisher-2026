import type { docs_v1 } from "googleapis";

export type DocSuggestionSnippet = {
  suggestionId: string;
  kind: "insertion" | "deletion";
  /** Human-readable payload: text for runs, or a short structural hint */
  content: string;
  startIndex?: number | null;
  endIndex?: number | null;
  /** Breadcrumb: body, tab, header, footer, footnote, etc. */
  section: string;
};

function pushElementSuggestionIds(
  insertions: string[] | null | undefined,
  deletions: string[] | null | undefined,
  singleInsertion: string | null | undefined,
  startIndex: number | null | undefined,
  endIndex: number | null | undefined,
  section: string,
  contentHint: string,
  acc: DocSuggestionSnippet[],
): void {
  for (const suggestionId of insertions ?? []) {
    acc.push({
      suggestionId,
      kind: "insertion",
      content: contentHint,
      startIndex,
      endIndex,
      section,
    });
  }
  for (const suggestionId of deletions ?? []) {
    acc.push({
      suggestionId,
      kind: "deletion",
      content: contentHint,
      startIndex,
      endIndex,
      section,
    });
  }
  if (singleInsertion) {
    acc.push({
      suggestionId: singleInsertion,
      kind: "insertion",
      content: contentHint,
      startIndex,
      endIndex,
      section,
    });
  }
}

function pushFromTextRun(
  el: docs_v1.Schema$ParagraphElement,
  section: string,
  acc: DocSuggestionSnippet[],
): void {
  const tr = el.textRun;
  if (!tr) return;
  const content = tr.content ?? "";
  pushElementSuggestionIds(
    tr.suggestedInsertionIds,
    tr.suggestedDeletionIds,
    null,
    el.startIndex,
    el.endIndex,
    section,
    content,
    acc,
  );
}

function walkParagraphElement(
  el: docs_v1.Schema$ParagraphElement,
  section: string,
  acc: DocSuggestionSnippet[],
): void {
  const si = el.startIndex;
  const ei = el.endIndex;
  if (el.textRun) {
    pushFromTextRun(el, section, acc);
    return;
  }
  if (el.autoText) {
    pushElementSuggestionIds(
      el.autoText.suggestedInsertionIds,
      el.autoText.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      "(autoText)",
      acc,
    );
    return;
  }
  if (el.columnBreak) {
    pushElementSuggestionIds(
      el.columnBreak.suggestedInsertionIds,
      el.columnBreak.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      "(columnBreak)",
      acc,
    );
    return;
  }
  if (el.equation) {
    pushElementSuggestionIds(
      el.equation.suggestedInsertionIds,
      el.equation.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      "(equation)",
      acc,
    );
    return;
  }
  if (el.footnoteReference) {
    pushElementSuggestionIds(
      el.footnoteReference.suggestedInsertionIds,
      el.footnoteReference.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      `(footnoteRef:${el.footnoteReference.footnoteId ?? "?"})`,
      acc,
    );
    return;
  }
  if (el.horizontalRule) {
    pushElementSuggestionIds(
      el.horizontalRule.suggestedInsertionIds,
      el.horizontalRule.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      "(horizontalRule)",
      acc,
    );
    return;
  }
  if (el.inlineObjectElement) {
    pushElementSuggestionIds(
      el.inlineObjectElement.suggestedInsertionIds,
      el.inlineObjectElement.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      `(inlineObjectElement:${el.inlineObjectElement.inlineObjectId ?? "?"})`,
      acc,
    );
    return;
  }
  if (el.pageBreak) {
    pushElementSuggestionIds(
      el.pageBreak.suggestedInsertionIds,
      el.pageBreak.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      "(pageBreak)",
      acc,
    );
    return;
  }
  if (el.person) {
    const p = el.person;
    const label =
      p.personProperties?.name ||
      p.personProperties?.email ||
      p.personId ||
      "person";
    pushElementSuggestionIds(
      p.suggestedInsertionIds,
      p.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      `(person:${label})`,
      acc,
    );
    return;
  }
  if (el.richLink) {
    const title = el.richLink.richLinkProperties?.title ?? "richLink";
    pushElementSuggestionIds(
      el.richLink.suggestedInsertionIds,
      el.richLink.suggestedDeletionIds,
      null,
      si,
      ei,
      section,
      `(richLink:${title})`,
      acc,
    );
  }
}

function walkParagraphElements(
  paragraph: docs_v1.Schema$Paragraph | undefined,
  section: string,
  acc: DocSuggestionSnippet[],
): void {
  for (const el of paragraph?.elements ?? []) {
    walkParagraphElement(el, section, acc);
  }
}

function walkStructuralElements(
  elements: docs_v1.Schema$StructuralElement[] | undefined,
  section: string,
  acc: DocSuggestionSnippet[],
): void {
  if (!elements?.length) return;
  for (const se of elements) {
    const si = se.startIndex;
    const ei = se.endIndex;
    if (se.sectionBreak) {
      const sb = se.sectionBreak;
      pushElementSuggestionIds(
        sb.suggestedInsertionIds,
        sb.suggestedDeletionIds,
        null,
        si,
        ei,
        section,
        "(sectionBreak)",
        acc,
      );
    } else if (se.table) {
      const t = se.table;
      pushElementSuggestionIds(
        t.suggestedInsertionIds,
        t.suggestedDeletionIds,
        null,
        si,
        ei,
        section,
        "(table)",
        acc,
      );
      for (const row of t.tableRows ?? []) {
        pushElementSuggestionIds(
          row.suggestedInsertionIds,
          row.suggestedDeletionIds,
          null,
          row.startIndex,
          row.endIndex,
          `${section} > tableRow`,
          "(tableRow)",
          acc,
        );
        for (const cell of row.tableCells ?? []) {
          pushElementSuggestionIds(
            cell.suggestedInsertionIds,
            cell.suggestedDeletionIds,
            null,
            cell.startIndex,
            cell.endIndex,
            `${section} > tableCell`,
            "(tableCell)",
            acc,
          );
          walkStructuralElements(cell.content, `${section} > tableCell`, acc);
        }
      }
    } else if (se.tableOfContents) {
      const toc = se.tableOfContents;
      pushElementSuggestionIds(
        toc.suggestedInsertionIds,
        toc.suggestedDeletionIds,
        null,
        si,
        ei,
        section,
        "(tableOfContents)",
        acc,
      );
      walkStructuralElements(toc.content, `${section} > toc`, acc);
    } else if (se.paragraph) {
      walkParagraphElements(se.paragraph, section, acc);
    }
  }
}

function walkInlineObjectMap(
  inlineObjects: Record<string, docs_v1.Schema$InlineObject> | null | undefined,
  sectionPrefix: string,
  acc: DocSuggestionSnippet[],
): void {
  for (const [oid, obj] of Object.entries(inlineObjects ?? {})) {
    const hint = `(inlineObject:${oid})`;
    pushElementSuggestionIds(
      undefined,
      obj.suggestedDeletionIds,
      obj.suggestedInsertionId ?? undefined,
      undefined,
      undefined,
      `${sectionPrefix} > ${hint}`,
      hint,
      acc,
    );
  }
}

function walkPositionedObjectMap(
  positionedObjects:
    | Record<string, docs_v1.Schema$PositionedObject>
    | null
    | undefined,
  sectionPrefix: string,
  acc: DocSuggestionSnippet[],
): void {
  for (const [pid, po] of Object.entries(positionedObjects ?? {})) {
    const hint = `(positionedObject:${pid})`;
    pushElementSuggestionIds(
      undefined,
      po.suggestedDeletionIds,
      po.suggestedInsertionId ?? undefined,
      undefined,
      undefined,
      `${sectionPrefix} > ${hint}`,
      hint,
      acc,
    );
  }
}

/** Headers, footers, footnotes, and floating objects on a tab (not `documentTab.body`). */
function walkDocumentTabAuxiliary(
  dt: docs_v1.Schema$DocumentTab | undefined,
  tabLabel: string,
  acc: DocSuggestionSnippet[],
): void {
  if (!dt) return;
  for (const [hid, h] of Object.entries(dt.headers ?? {})) {
    walkStructuralElements(h.content, `${tabLabel} > header:${hid}`, acc);
  }
  for (const [fid, f] of Object.entries(dt.footers ?? {})) {
    walkStructuralElements(f.content, `${tabLabel} > footer:${fid}`, acc);
  }
  for (const [fnid, fn] of Object.entries(dt.footnotes ?? {})) {
    walkStructuralElements(fn.content, `${tabLabel} > footnote:${fnid}`, acc);
  }
  walkInlineObjectMap(dt.inlineObjects, tabLabel, acc);
  walkPositionedObjectMap(dt.positionedObjects, tabLabel, acc);
}

/**
 * Legacy top-level maps (pre-tabs): only used when the document has no `tabs` array,
 * so we do not duplicate tab content that already lives under `documentTab`.
 */
function walkLegacyTopLevelFragments(
  doc: docs_v1.Schema$Document,
  acc: DocSuggestionSnippet[],
): void {
  if (doc.tabs?.length) return;
  const prefix = "legacyDocument";
  for (const [hid, h] of Object.entries(doc.headers ?? {})) {
    walkStructuralElements(h.content, `${prefix} > header:${hid}`, acc);
  }
  for (const [fid, f] of Object.entries(doc.footers ?? {})) {
    walkStructuralElements(f.content, `${prefix} > footer:${fid}`, acc);
  }
  for (const [fnid, fn] of Object.entries(doc.footnotes ?? {})) {
    walkStructuralElements(fn.content, `${prefix} > footnote:${fnid}`, acc);
  }
  walkInlineObjectMap(doc.inlineObjects, prefix, acc);
  walkPositionedObjectMap(doc.positionedObjects, prefix, acc);
}

function walkTabs(
  tabs: docs_v1.Schema$Tab[] | undefined,
  acc: DocSuggestionSnippet[],
): void {
  if (!tabs?.length) return;
  for (const tab of tabs) {
    const tabId = tab.tabProperties?.tabId ?? "unknownTab";
    const title = tab.tabProperties?.title;
    const label =
      title && title.length > 0
        ? `tab:${tabId} (${title})`
        : `tab:${tabId}`;
    walkStructuralElements(tab.documentTab?.body?.content, label, acc);
    walkDocumentTabAuxiliary(tab.documentTab, label, acc);
    walkTabs(tab.childTabs, acc);
  }
}

/** Collect suggested insertions/deletions from a `documents.get` response (use `suggestionsViewMode: SUGGESTIONS_INLINE`). */
export function extractSuggestionSnippets(
  doc: docs_v1.Schema$Document,
): DocSuggestionSnippet[] {
  const acc: DocSuggestionSnippet[] = [];
  if (doc.body?.content) {
    walkStructuralElements(doc.body.content, "body", acc);
  }
  walkLegacyTopLevelFragments(doc, acc);
  walkTabs(doc.tabs, acc);
  acc.sort((a, b) => {
    const sa = a.startIndex ?? 0;
    const sb = b.startIndex ?? 0;
    if (sa !== sb) return sa - sb;
    return a.suggestionId.localeCompare(b.suggestionId);
  });
  return acc;
}
