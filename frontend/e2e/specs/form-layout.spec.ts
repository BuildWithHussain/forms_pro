import { test, expect } from "../fixtures/test-data.fixture";
import { FormBuilderPage } from "../helpers/form-builder";
import { SubmissionPage } from "../helpers/submission";

// Helper: set a form's field list via REST so the builder loads with a known
// row/column/cell layout. Mirrors the pattern used in heading-field.spec.ts.
async function setFormFields(
  apiContext: import("@playwright/test").APIRequestContext,
  formId: string,
  fields: Array<{
    label: string;
    fieldtype?: string;
    row_index: number;
    column_index?: number;
    cell_index?: number;
  }>
) {
  await apiContext.put(`/api/resource/Form/${formId}`, {
    data: {
      fields: fields.map((f, i) => ({
        idx: i + 1,
        fieldtype: f.fieldtype ?? "Data",
        label: f.label,
        fieldname: f.label.toLowerCase(),
        reqd: 0,
        row_index: f.row_index,
        column_index: f.column_index ?? 0,
        cell_index: f.cell_index ?? 0,
      })),
    },
  });
}

test.describe("Multi-column form layout", () => {
  test("cell stacks into existing column on drag", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0 },
      { label: "B", row_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    // Sanity: starting layout is 2 rows, 1 column each, 1 cell each
    await builder.waitForFields(["A", "B"]);
    expect(await builder.rowCount()).toBe(2);

    await builder.dragFieldOntoCell("B", "A", "above");

    // After drag: 1 row, 1 column, 2 cells stacked in (row 0, col 0)
    await expect.poll(() => builder.rowCount()).toBe(1);
    await expect.poll(() => builder.columnCount(0)).toBe(1);
    await expect.poll(() => builder.cellCount(0, 0)).toBe(2);
  });

  test("column drop zone creates new column", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0 },
      { label: "B", row_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    await builder.waitForFields(["A", "B"]);

    // Drop B into the column drop zone right of A (row 0, col 1)
    await builder.dragFieldToColumnZone("B", 0, 1);

    await expect.poll(() => builder.rowCount()).toBe(1);
    await expect.poll(() => builder.columnCount(0)).toBe(2);
    await expect.poll(() => builder.cellCount(0, 0)).toBe(1);
    await expect.poll(() => builder.cellCount(0, 1)).toBe(1);
  });

  test("row drop zone creates new row", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    // 2-column row of A, B in row 0
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0, column_index: 0 },
      { label: "B", row_index: 0, column_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    await builder.waitForFields(["A", "B"]);
    expect(await builder.columnCount(0)).toBe(2);

    // Drop B above current row — B becomes row 0, A pushed to row 1
    await builder.dragFieldToRowZone("B", 0);

    await expect.poll(() => builder.rowCount()).toBe(2);
    await expect.poll(() => builder.columnCount(0)).toBe(1);
    await expect.poll(() => builder.columnCount(1)).toBe(1);
  });

  test("eject moves cell to new row", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    // 2-cell column: A on top (cell 0), B below (cell 1) — same row, same col
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0, column_index: 0, cell_index: 0 },
      { label: "B", row_index: 0, column_index: 0, cell_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    await builder.waitForFields(["A", "B"]);
    expect(await builder.cellCount(0, 0)).toBe(2);

    // Eject A — A moves to its own row, B stays put
    await builder.ejectField("A");

    await expect.poll(() => builder.rowCount()).toBe(2);
    // No multi-cell column should remain
    const rows = await builder.rowCount();
    for (let r = 0; r < rows; r++) {
      const cols = await builder.columnCount(r);
      for (let c = 0; c < cols; c++) {
        expect(await builder.cellCount(r, c)).toBe(1);
      }
    }
  });

  test("cross-row drag collapses source column", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    // 2 rows x 2 cols: A, B / C, D
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0, column_index: 0 },
      { label: "B", row_index: 0, column_index: 1 },
      { label: "C", row_index: 1, column_index: 0 },
      { label: "D", row_index: 1, column_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    await builder.waitForFields(["A", "B", "C", "D"]);
    expect(await builder.columnCount(0)).toBe(2);
    expect(await builder.columnCount(1)).toBe(2);

    // Stack B onto C — moves B into row 1, col 0 (cell 0 above C)
    await builder.dragFieldOntoCell("B", "C", "above");

    // Row 0 collapses to 1 column (only A); row 1 still has 2 columns
    await expect.poll(() => builder.rowCount()).toBe(2);
    await expect.poll(() => builder.columnCount(0)).toBe(1);
    await expect.poll(() => builder.columnCount(1)).toBe(2);
    await expect.poll(() => builder.cellCount(1, 0)).toBe(2);
  });

  test("within-column reorder renumbers cell_index", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    // 2-cell column: A on top, B on bottom
    await setFormFields(apiContext, formId, [
      { label: "A", row_index: 0, column_index: 0, cell_index: 0 },
      { label: "B", row_index: 0, column_index: 0, cell_index: 1 },
    ]);

    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });

    await builder.waitForFields(["A", "B"]);

    // Drag B above A — DOM order should flip to B, A
    await builder.dragFieldOntoCell("B", "A", "above");

    const labelsInColumn = () =>
      page
        .locator(
          '[data-form-builder-component="cell-column"][data-row-index="0"][data-col-index="0"] [data-form-builder-component="field-card"]'
        )
        .evaluateAll((els) =>
          els.map((e) => (e as HTMLElement).getAttribute("data-field-label"))
        );

    await expect.poll(labelsInColumn).toEqual(["B", "A"]);
  });

  test("mobile viewport stacks columns vertically", async ({
    browser,
    createPublishedForm,
    apiContext,
  }) => {
    const { formId, route } = await createPublishedForm();
    // 2-column row of A, B (use Data fieldtype so they render as inputs)
    await apiContext.put(`/api/resource/Form/${formId}`, {
      data: {
        fields: [
          {
            idx: 1,
            fieldtype: "Data",
            label: "A",
            fieldname: "a",
            row_index: 0,
            column_index: 0,
            cell_index: 0,
          },
          {
            idx: 2,
            fieldtype: "Data",
            label: "B",
            fieldname: "b",
            row_index: 0,
            column_index: 1,
            cell_index: 0,
          },
        ],
      },
    });

    // Mobile viewport
    const guestCtx = await browser.newContext({
      viewport: { width: 375, height: 800 },
    });
    const guestPage = await guestCtx.newPage();
    const submission = new SubmissionPage(guestPage);
    await submission.goto(route);
    await guestPage.waitForLoadState("networkidle");

    const row = guestPage.locator('[data-form-renderer-component="form-row"]');
    await expect(row).toBeVisible({ timeout: 15000 });

    const flexDirection = await row.evaluate(
      (el) => getComputedStyle(el as HTMLElement).flexDirection
    );
    expect(flexDirection).toBe("column");

    await guestCtx.close();
  });

  test("hidden field unmounts, no empty column", async ({
    browser,
    createPublishedForm,
    apiContext,
  }) => {
    const { formId, route } = await createPublishedForm();

    // 2-column row: A (col 0), B (col 1). A carries a conditional rule that
    // hides B whenever A is empty (it always is on first render), exercising
    // the "hide a column entirely when its only field is hidden" path.
    const conditionalLogic = JSON.stringify({
      target_field: "b",
      conditions: [{ fieldname: "a", operator: "Is Empty", value: "" }],
      action: "Hide Field",
    });

    await apiContext.put(`/api/resource/Form/${formId}`, {
      data: {
        fields: [
          {
            idx: 1,
            fieldtype: "Data",
            label: "A",
            fieldname: "a",
            row_index: 0,
            column_index: 0,
            cell_index: 0,
            conditional_logic: conditionalLogic,
          },
          {
            idx: 2,
            fieldtype: "Data",
            label: "B",
            fieldname: "b",
            row_index: 0,
            column_index: 1,
            cell_index: 0,
          },
        ],
      },
    });

    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submission = new SubmissionPage(guestPage);
    await submission.goto(route);

    // Wait for the Submit button — confirms the renderer mounted past
    // initial load (the form layout is reactive to the API fetch).
    await expect(guestPage.getByRole("button", { name: "Submit" })).toBeVisible(
      { timeout: 10000 }
    );

    // Row should render with exactly one column (the one holding A); the
    // column wrapping B must be unmounted (v-if), not just emptied.
    const row = guestPage.locator('[data-form-renderer-component="form-row"]');
    await expect(row).toHaveCount(1);
    const columns = row.locator('[data-form-renderer-component="form-column"]');
    await expect(columns).toHaveCount(1);

    // Only A's input should render — B is unmounted by the conditional rule
    // (frappe-ui's FormControl doesn't expose `name`, so count text inputs
    // inside the form column instead).
    await expect(columns.locator("input[type='text']")).toHaveCount(1);

    await guestCtx.close();
  });
});
