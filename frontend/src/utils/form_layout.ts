/**
 * Pure layout-grid helpers — no component imports, safe for unit tests.
 *
 * The layout invariant: every field carries (row_index, column_index,
 * cell_index) and row_index is globally unique per row across the whole
 * form, including Page Breaks.
 */
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import type { FormField } from "@/types/formfield";

export const isHeading = (fieldtype: Fieldtype): boolean => {
  return [
    Fieldtype.HEADING_1,
    Fieldtype.HEADING_2,
    Fieldtype.HEADING_3,
  ].includes(fieldtype);
};

export const isPageBreak = (fieldtype: Fieldtype): boolean => {
  return fieldtype === Fieldtype.PAGE_BREAK;
};

export const isDisplayOnly = (fieldtype: Fieldtype): boolean => {
  return isHeading(fieldtype) || isPageBreak(fieldtype);
};

export function scrubFieldname(label: string) {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_") // replace non-alphanumeric with underscores
    .replace(/^_+|_+$/g, "") // trim leading/trailing underscores
    .replace(/_{2,}/g, "_"); // collapse multiple underscores
}

export function lastRowIndex(fields: FormField[]): number {
  return fields.reduce((m, f) => Math.max(m, f.row_index ?? 0), -1);
}

/**
 * Normalizes the layout grid in place: closes row gaps, renumbers
 * column_index within each row, and cell_index within each cell.
 */
export function compact(fields: FormField[]): void {
  if (!fields.length) return;

  // Remap row_index values to 0..N-1 (closes gaps left by deletions/moves)
  const distinctRows = [...new Set(fields.map((f) => f.row_index ?? 0))].sort(
    (a, b) => a - b
  );
  const rowRemap = new Map(distinctRows.map((r, i) => [r, i]));
  for (const f of fields) {
    f.row_index = rowRemap.get(f.row_index ?? 0) ?? 0;
  }

  // Remap distinct column_index values within each row to 0..M-1
  // (cells sharing a column_index stay grouped — multi-cell columns preserved)
  const rowColsMap = new Map<number, Set<number>>();
  for (const f of fields) {
    const r = f.row_index!;
    if (!rowColsMap.has(r)) rowColsMap.set(r, new Set());
    rowColsMap.get(r)!.add(f.column_index ?? 0);
  }
  const colRemapByRow = new Map<number, Map<number, number>>();
  for (const [r, cols] of rowColsMap) {
    const sorted = [...cols].sort((a, b) => a - b);
    colRemapByRow.set(r, new Map(sorted.map((c, i) => [c, i])));
  }
  for (const f of fields) {
    f.column_index =
      colRemapByRow.get(f.row_index!)!.get(f.column_index ?? 0) ?? 0;
  }

  // Renumber cell_index within each (row, column) to 0..K-1
  const cellMap = new Map<string, FormField[]>();
  for (const f of fields) {
    const key = `${f.row_index}-${f.column_index}`;
    if (!cellMap.has(key)) cellMap.set(key, []);
    cellMap.get(key)!.push(f);
  }
  for (const cells of cellMap.values()) {
    cells
      .sort((a, b) => (a.cell_index ?? 0) - (b.cell_index ?? 0))
      .forEach((f, i) => {
        f.cell_index = i;
      });
  }
}
