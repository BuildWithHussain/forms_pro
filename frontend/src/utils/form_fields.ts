import {
  FIELD_TYPE_DEFINITIONS,
  FIELD_TYPE_MAP,
  getFieldTypeDef,
} from "@/config/fieldTypes";
import type { FieldTypeDefinition } from "@/config/fieldTypes";
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import type { FormField } from "@/types/formfield";
import type { Component } from "vue";

// Re-export the registry under the names the rest of the codebase uses
export {
  FIELD_TYPE_DEFINITIONS as formFields,
  getFieldTypeDef,
  FIELD_TYPE_MAP,
};
export type { FieldTypeDefinition as FormFields };

// Subset type used by RenderField.vue
export type FormFieldType = {
  component: Component;
  props: Record<string, unknown>;
};

// Maps Frappe DocType fieldtypes to the equivalent Forms Pro fieldtype.
// Used when importing fields from an existing DocType into a form.
export const mapDoctypeFieldForForm = (
  fieldtype: string
): string | undefined => {
  const FRAPPE_TO_FORM_TYPE: Partial<Record<string, Fieldtype>> = {
    Autocomplete: Fieldtype.DATA,
    Attach: Fieldtype.ATTACH,
    "Attach Image": Fieldtype.ATTACH,
    Check: Fieldtype.CHECKBOX,
    Currency: Fieldtype.NUMBER,
    Data: Fieldtype.DATA,
    Date: Fieldtype.DATE,
    Datetime: Fieldtype.DATE_TIME,
    Float: Fieldtype.NUMBER,
    "HTML Editor": Fieldtype.TEXT_EDITOR,
    Int: Fieldtype.NUMBER,
    Link: Fieldtype.LINK,
    "Long Text": Fieldtype.TEXTAREA,
    "Markdown Editor": Fieldtype.TEXT_EDITOR,
    Password: Fieldtype.PASSWORD,
    Percent: Fieldtype.NUMBER,
    Phone: Fieldtype.PHONE,
    Rating: Fieldtype.RATING,
    Select: Fieldtype.SELECT,
    "Small Text": Fieldtype.TEXTAREA,
    Table: Fieldtype.TABLE,
    Text: Fieldtype.TEXTAREA,
    "Text Editor": Fieldtype.TEXT_EDITOR,
    Time: Fieldtype.TIME_PICKER,
  };

  return FRAPPE_TO_FORM_TYPE[fieldtype];
};

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
