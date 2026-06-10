import { expect, type APIRequestContext } from "@playwright/test";

export type SeedField = {
  label: string;
  fieldtype?: string;
  fieldname?: string;
  reqd?: 0 | 1;
  hidden?: 0 | 1;
  conditional_logic?: string;
  row_index?: number;
  column_index?: number;
  cell_index?: number;
};

function defaultFieldname(label: string): string {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

// Replace a form's full field list via REST so the builder/public page load a
// known layout. row_index defaults to the array position, which keeps every
// field on its own row — fine for step tests, which don't care about columns.
export async function setFormFields(
  apiContext: APIRequestContext,
  formId: string,
  fields: SeedField[]
) {
  const res = await apiContext.put(`/api/resource/Form/${formId}`, {
    data: {
      fields: fields.map((f, i) => ({
        idx: i + 1,
        fieldtype: f.fieldtype ?? "Data",
        label: f.label,
        fieldname: f.fieldname ?? defaultFieldname(f.label),
        reqd: f.reqd ?? 0,
        hidden: f.hidden ?? 0,
        conditional_logic: f.conditional_logic ?? "",
        row_index: f.row_index ?? i,
        column_index: f.column_index ?? 0,
        cell_index: f.cell_index ?? 0,
      })),
    },
  });
  // Fail loudly here rather than as a confusing locator timeout downstream.
  expect(
    res.ok(),
    `setFormFields PUT failed: ${res.status()} ${await res.text()}`
  ).toBeTruthy();
}

export function pageBreak(label = "", fieldname?: string): SeedField {
  return {
    label,
    fieldtype: "Page Break",
    fieldname: fieldname ?? (label ? defaultFieldname(label) : undefined),
  };
}

// 3 steps: Basics(Full Name) / Contact(Work Email) / Final(Notes).
// Leading Page Break labels step 1.
export function threeStepFields(): SeedField[] {
  return [
    pageBreak("Basics", "pb_basics"),
    { label: "Full Name" },
    pageBreak("Contact", "pb_contact"),
    { label: "Work Email" },
    pageBreak("Final", "pb_final"),
    { label: "Notes" },
  ];
}

// 2 steps with NO leading Page Break: step 1 is unlabeled in data
// (builder shows fallback "Step 1"), Page Break labels step 2.
export function twoStepFieldsNoLeadingPB(): SeedField[] {
  return [
    { label: "Full Name" },
    pageBreak("Details", "pb_details"),
    { label: "Notes" },
  ];
}
