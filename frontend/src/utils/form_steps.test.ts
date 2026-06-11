import { describe, it, expect } from "vitest";
import type { FormField } from "@/types/formfield";
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import {
  insertFieldAtStepEnd,
  renameStep,
  groupFieldsIntoSteps,
} from "./form_steps";

function dataField(row: number, fieldname: string): FormField {
  return {
    idx: 0,
    fieldtype: Fieldtype.DATA,
    label: fieldname,
    fieldname,
    row_index: row,
    column_index: 0,
    cell_index: 0,
  } as FormField;
}

function pageBreak(row: number, label: string): FormField {
  return {
    idx: 0,
    fieldtype: Fieldtype.PAGE_BREAK,
    label,
    fieldname: label.toLowerCase().replace(/\s+/g, "_"),
    row_index: row,
    column_index: 0,
    cell_index: 0,
  } as FormField;
}

function gridTuples(fields: FormField[]): string[] {
  return fields.map((f) => `${f.row_index}-${f.column_index}-${f.cell_index}`);
}

function expectUniqueRows(fields: FormField[]) {
  const rows = fields.map((f) => f.row_index);
  expect(new Set(rows).size).toBe(rows.length);
}

describe("insertFieldAtStepEnd", () => {
  it("appends to the end with the next row on a single-step form", () => {
    const fields = [dataField(0, "a"), dataField(1, "b")];
    const newField = dataField(0, "new");

    insertFieldAtStepEnd(fields, newField, 0, false);

    expect(fields[2]).toBe(newField);
    expect(newField.row_index).toBe(2);
    expectUniqueRows(fields);
  });

  it("gives a unique row when adding to an empty trailing step", () => {
    // Step 0: rows 0,1 — Step 1: empty (just the Page Break at row 2)
    const fields = [
      dataField(0, "a"),
      dataField(1, "b"),
      pageBreak(2, "Step 2"),
    ];
    const newField = dataField(0, "new");

    insertFieldAtStepEnd(fields, newField, 1, true);

    expect(fields[3]).toBe(newField);
    expect(newField.row_index).toBe(3);
    expectUniqueRows(fields);
  });

  it("targets the right step when the form has a leading Page Break", () => {
    // Leading PB names step 0: Step "One" = [a], "Two" = [b], "Three" = [c]
    const fields = [
      pageBreak(0, "One"),
      dataField(1, "a"),
      pageBreak(2, "Two"),
      dataField(3, "b"),
      pageBreak(4, "Three"),
      dataField(5, "c"),
    ];

    const intoFirst = dataField(0, "new_first");
    insertFieldAtStepEnd(fields, intoFirst, 0, true);
    let steps = groupFieldsIntoSteps(fields);
    expect(steps[0].fields.map((f) => f.fieldname)).toEqual(["a", "new_first"]);

    const intoLast = dataField(0, "new_last");
    insertFieldAtStepEnd(fields, intoLast, 2, true);
    steps = groupFieldsIntoSteps(fields);
    expect(steps[2].fields.map((f) => f.fieldname)).toEqual(["c", "new_last"]);
    expectUniqueRows(fields);
  });

  it("shifts later steps' rows when inserting into a middle step", () => {
    // Step 0: row 0 — Step 1: row 2 — Step 2: row 4
    const fields = [
      dataField(0, "a"),
      pageBreak(1, "Step 2"),
      dataField(2, "b"),
      pageBreak(3, "Step 3"),
      dataField(4, "c"),
    ];
    const newField = dataField(0, "new");

    insertFieldAtStepEnd(fields, newField, 1, true);

    // Inserted just before the "Step 3" Page Break
    expect(fields[3]).toBe(newField);
    expect(newField.row_index).toBe(3);
    expectUniqueRows(fields);
    // Step membership intact
    const steps = groupFieldsIntoSteps(fields);
    expect(steps[1].fields.map((f) => f.fieldname)).toEqual(["b", "new"]);
    expect(steps[2].fields.map((f) => f.fieldname)).toEqual(["c"]);
  });
});

describe("renameStep step 0 without a leading Page Break", () => {
  it("inserts the leading Page Break without colliding grid positions", () => {
    const fields = [dataField(0, "a"), dataField(1, "b")];

    renameStep(fields, 0, "Intro");

    expect(fields[0].fieldtype).toBe(Fieldtype.PAGE_BREAK);
    expect(fields[0].label).toBe("Intro");
    const tuples = gridTuples(fields);
    expect(new Set(tuples).size).toBe(tuples.length);

    const steps = groupFieldsIntoSteps(fields);
    expect(steps).toHaveLength(1);
    expect(steps[0].label).toBe("Intro");
    expect(steps[0].fields.map((f) => f.fieldname)).toEqual(["a", "b"]);
  });
});
