import type { FormField } from "@/types/formfield";
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import {
  isPageBreak,
  scrubFieldname,
  lastRowIndex,
  compact,
} from "@/utils/form_layout";

export type FormStep = {
  label: string;
  fields: FormField[];
};

export type GroupFieldsOptions = {
  /** Label for a step whose Page Break has no label (1-based step number). Defaults to "". */
  labelFallback?: (stepNumber: number) => string;
  /** Push the trailing step even when the form has no fields (guarantees >= 1 step). */
  alwaysIncludeTrailing?: boolean;
};

/**
 * Groups a flat field list into steps, splitting on Page Break fields.
 * A Page Break's label names the step that follows it; a leading Page Break
 * names the first step instead of creating an empty one.
 */
export function groupFieldsIntoSteps(
  fields: FormField[],
  options: GroupFieldsOptions = {}
): FormStep[] {
  const { labelFallback = () => "", alwaysIncludeTrailing = false } = options;
  const result: FormStep[] = [];
  let current: FormField[] = [];
  let nextLabel = "";
  let isFirst = true;

  for (const field of fields) {
    if (isPageBreak(field.fieldtype)) {
      if (isFirst) {
        nextLabel = field.label || "";
        isFirst = false;
        continue;
      }
      result.push({
        label: nextLabel || labelFallback(result.length + 1),
        fields: current,
      });
      current = [];
      nextLabel = field.label || "";
      continue;
    }
    isFirst = false;
    current.push(field);
  }

  if (alwaysIncludeTrailing || current.length > 0 || result.length > 0) {
    result.push({
      label: nextLabel || labelFallback(result.length + 1),
      fields: current,
    });
  }

  return result;
}

/**
 * Index in `fields` of the Page Break that starts step `stepIndex`.
 * A leading Page Break belongs to step 0, so it shifts the target by one.
 * Returns -1 when the step has no Page Break (e.g. step 0 of an unlabeled form).
 */
export function findStepPageBreakIndex(
  fields: FormField[],
  stepIndex: number
): number {
  const hasLeadingPB = fields[0] ? isPageBreak(fields[0].fieldtype) : false;
  const target = stepIndex + (hasLeadingPB ? 1 : 0);
  if (target === 0) return -1;
  let pbCount = 0;
  for (let i = 0; i < fields.length; i++) {
    if (isPageBreak(fields[i].fieldtype)) {
      pbCount++;
      if (pbCount === target) return i;
    }
  }
  return -1;
}

/**
 * Index in `fields` just past the last field of step `activeIndex`,
 * i.e. where a new field for that step should be inserted.
 */
export function getActiveStepEndIndex(
  fields: FormField[],
  activeIndex: number,
  isMultiStep: boolean
): number {
  if (!isMultiStep) return fields.length;

  // A leading Page Break names step 0 rather than ending it, so the
  // step's end is the (activeIndex + 1)-th Page Break in that case.
  const hasLeadingPB = fields[0] ? isPageBreak(fields[0].fieldtype) : false;
  const target = activeIndex + (hasLeadingPB ? 1 : 0);

  let pbCount = 0;
  for (let i = 0; i < fields.length; i++) {
    if (isPageBreak(fields[i].fieldtype)) {
      if (pbCount === target) return i;
      pbCount++;
    }
  }
  return fields.length;
}

/**
 * Inserts `field` at the end of step `stepIndex`, assigning it the next
 * row after everything before the insertion point and shifting the rows
 * of all later fields to keep row_index globally unique.
 */
export function insertFieldAtStepEnd(
  fields: FormField[],
  field: FormField,
  stepIndex: number,
  isMultiStep: boolean
): void {
  const insertAt = getActiveStepEndIndex(fields, stepIndex, isMultiStep);
  const newRowIndex = lastRowIndex(fields.slice(0, insertAt)) + 1;
  for (const f of fields.slice(insertAt)) {
    f.row_index = (f.row_index ?? 0) + 1;
  }
  field.row_index = newRowIndex;
  field.column_index = 0;
  field.cell_index = 0;
  fields.splice(insertAt, 0, field);
}

/**
 * Removes a leading Page Break when it is the only one left —
 * a single-step form doesn't need a step label field.
 */
export function stripOrphanedLeadingPageBreak(fields: FormField[]): void {
  const hasLeadingPB = fields[0] ? isPageBreak(fields[0].fieldtype) : false;
  const pbCount = fields.filter((f) => isPageBreak(f.fieldtype)).length;
  if (hasLeadingPB && pbCount === 1) {
    fields.splice(0, 1);
  }
}

/** Appends a new step (Page Break) after the last field. */
export function appendStep(fields: FormField[], stepCount: number): void {
  fields.push({
    idx: fields.length + 1,
    fieldtype: Fieldtype.PAGE_BREAK,
    label: `Step ${stepCount + 1}`,
    fieldname: scrubFieldname(`section_${stepCount + 1}`),
    row_index: lastRowIndex(fields) + 1,
    column_index: 0,
    cell_index: 0,
  } as FormField);
}

/**
 * Removes step `index`'s Page Break, merging its fields into the previous
 * step (their rows are re-offset to follow the previous step's last row).
 * Step 0 cannot be removed.
 */
export function removeStepKeepFields(
  fields: FormField[],
  steps: FormStep[],
  index: number
): void {
  if (index <= 0) return;

  const pbIdx = findStepPageBreakIndex(fields, index);
  if (pbIdx === -1) return;

  const prevFields = steps[index - 1]?.fields ?? [];
  const movedFields = steps[index]?.fields ?? [];

  const maxPrevRow = prevFields.reduce(
    (max, f) => Math.max(max, f.row_index ?? 0),
    -1
  );
  const minMovedRow = movedFields.reduce(
    (min, f) => Math.min(min, f.row_index ?? 0),
    Infinity
  );

  if (movedFields.length > 0 && isFinite(minMovedRow)) {
    const offset = maxPrevRow - minMovedRow + 1;
    for (const f of movedFields) {
      f.row_index = (f.row_index ?? 0) + offset;
    }
  }

  fields.splice(pbIdx, 1);
  stripOrphanedLeadingPageBreak(fields);
  compact(fields);
}

/**
 * Removes step `index` along with all its fields and its Page Break.
 * Step 0 cannot be removed.
 */
export function removeStepWithFields(
  fields: FormField[],
  steps: FormStep[],
  index: number
): void {
  if (index <= 0) return;

  const stepFields = steps[index]?.fields ?? [];
  const fieldSet = new Set(stepFields);
  const pbIdx = findStepPageBreakIndex(fields, index);

  const toRemove = new Set<number>();
  if (pbIdx !== -1) toRemove.add(pbIdx);
  for (let i = 0; i < fields.length; i++) {
    if (fieldSet.has(fields[i])) toRemove.add(i);
  }

  for (const i of [...toRemove].sort((a, b) => b - a)) {
    fields.splice(i, 1);
  }

  stripOrphanedLeadingPageBreak(fields);
  compact(fields);
}

/**
 * Renames step `index` by relabeling its Page Break. Renaming step 0 of a
 * form without a leading Page Break inserts one to carry the label.
 */
export function renameStep(
  fields: FormField[],
  index: number,
  newLabel: string
): void {
  if (index === 0 && (!fields[0] || !isPageBreak(fields[0].fieldtype))) {
    // Make room at row 0 — existing fields shift down so the new Page
    // Break doesn't collide with them in the layout grid.
    for (const f of fields) {
      f.row_index = (f.row_index ?? 0) + 1;
    }
    fields.unshift({
      idx: 0,
      fieldtype: Fieldtype.PAGE_BREAK,
      label: newLabel,
      fieldname: scrubFieldname("section_1"),
      row_index: 0,
      column_index: 0,
      cell_index: 0,
    } as FormField);
    compact(fields);
    return;
  }

  const pbIdx = findStepPageBreakIndex(fields, index);
  if (pbIdx !== -1) {
    fields[pbIdx].label = newLabel;
  }
}
