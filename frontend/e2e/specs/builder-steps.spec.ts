import { test, expect } from "../fixtures/test-data.fixture";
import { FormBuilderPage } from "../helpers/form-builder";
import {
  setFormFields,
  threeStepFields,
  twoStepFieldsNoLeadingPB,
  pageBreak,
} from "../helpers/form-fields";

test.describe("Builder step navigation", () => {
  test("multi-step form renders one tab per step with first active", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await expect(builder.stepTab("Basics")).toBeVisible();
    await expect(builder.stepTab("Contact")).toBeVisible();
    await expect(builder.stepTab("Final")).toBeVisible();
    await expect(builder.activeStepTab()).toHaveText(/Basics/);
  });

  test("switching steps shows only that step's fields", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.switchToStep("Contact");
    await expect(builder.fieldCard("Work Email")).toBeVisible();
    await expect(builder.fieldCard("Full Name")).toHaveCount(0);
  });

  test("single-step form shows only Add Step button, no tabs", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, [{ label: "Solo Field" }]);
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Solo Field"]);

    await expect(
      builder.stepNav().getByRole("button", { name: "Add Step" })
    ).toBeVisible();
    await expect(builder.activeStepTab()).toHaveCount(0);
  });

  test("add step appends a new tab and activates it", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.addStep();
    await expect(builder.stepTab("Step 4")).toBeVisible();
    await expect(builder.activeStepTab()).toHaveText(/Step 4/);
    // New step is empty -> canvas shows the empty hint
    await expect(builder.canvasEmptyState()).toBeVisible();
  });

  test("step mutations mark the form unsaved", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.addStep();
    await expect(page.getByText("Unsaved", { exact: true })).toBeVisible();
  });

  test("rename step via double-click", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.renameStep("Contact", "Reach Me");
    await expect(builder.stepTab("Reach Me")).toBeVisible();
    await expect(builder.stepTab("Contact")).toHaveCount(0);
  });

  test("escape cancels rename", async ({ page, createForm, apiContext }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.stepTab("Contact").dblclick();
    const input = builder.stepNav().getByRole("textbox");
    await input.fill("Nope");
    await input.press("Escape");
    await expect(builder.stepTab("Contact")).toBeVisible();
    await expect(builder.stepTab("Nope")).toHaveCount(0);
  });

  test("rename first step of form without leading page break keeps step count", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, twoStepFieldsNoLeadingPB());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    // Step 1 has the fallback label since there is no leading Page Break
    await expect(builder.stepTab("Step 1")).toBeVisible();
    await builder.renameStep("Step 1", "Intro");

    await expect(builder.stepTab("Intro")).toBeVisible();
    await expect(builder.stepTab("Details")).toBeVisible();
    // Still exactly 2 steps: Intro, Details (+ Add Step button, which has no label match)
    await expect(builder.stepTab("Step 3")).toHaveCount(0);
  });

  test("first step has no remove control", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await expect(builder.removeStepControl("Basics")).toHaveCount(0);
    await expect(builder.removeStepControl("Contact")).toHaveCount(1);
  });

  test("remove step keeping fields merges them into previous step", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.removeStep("Contact", "keep");

    await expect(builder.stepTab("Contact")).toHaveCount(0);
    // Step 1 now holds both its own field and the merged one
    await expect(builder.fieldCard("Full Name")).toBeVisible();
    await expect(builder.fieldCard("Work Email")).toBeVisible();
    // Final step untouched
    await builder.switchToStep("Final");
    await expect(builder.fieldCard("Notes")).toBeVisible();
  });

  test("remove step with fields deletes the fields", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.removeStep("Contact", "delete");

    await expect(builder.stepTab("Contact")).toHaveCount(0);
    // Field gone from every remaining step
    await expect(builder.fieldCard("Work Email")).toHaveCount(0);
    await builder.switchToStep("Final");
    await expect(builder.fieldCard("Work Email")).toHaveCount(0);
  });

  test("removing an empty step skips the confirmation dialog", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, [
      pageBreak("Basics", "pb_basics"),
      { label: "Full Name" },
      pageBreak("Empty Step", "pb_empty"),
    ]);
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.removeStep("Empty Step"); // no mode: expects no dialog
    await expect(builder.stepTab("Empty Step")).toHaveCount(0);
  });

  test("removing the active last step clamps selection to previous step", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.switchToStep("Final");
    await builder.removeStep("Final", "delete");

    await expect(builder.activeStepTab()).toHaveText(/Contact/);
    await expect(builder.fieldCard("Work Email")).toBeVisible();
  });

  test("removing down to one step collapses the step nav", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, [
      pageBreak("Basics", "pb_basics"),
      { label: "Full Name" },
      pageBreak("Extra", "pb_extra"),
      { label: "Notes" },
    ]);
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.removeStep("Extra", "keep");

    // Back to single-step mode: tabs gone, lone Add Step button shown
    await expect(builder.activeStepTab()).toHaveCount(0);
    await expect(
      builder.stepNav().getByRole("button", { name: "Add Step" })
    ).toBeVisible();
    // Orphaned leading Page Break was stripped; both fields remain
    await expect(builder.fieldCard("Full Name")).toBeVisible();
    await expect(builder.fieldCard("Notes")).toBeVisible();
  });

  test("steps persist through save and reload", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId); // fills title + saves (needed before later save)
    await builder.waitForFields(["Full Name"]);

    await builder.renameStep("Contact", "Reach Me");
    await builder.addStep(); // "Step 4"
    await builder.save();

    await page.reload();
    await builder.waitForFields(["Full Name"]);
    await expect(builder.stepTab("Basics")).toBeVisible();
    await expect(builder.stepTab("Reach Me")).toBeVisible();
    await expect(builder.stepTab("Final")).toBeVisible();
    await expect(builder.stepTab("Step 4")).toBeVisible();
  });

  test("palette field is added to the active step", async ({
    page,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const builder = new FormBuilderPage(page);
    await builder.goto(formId, { skipTitleFill: true });
    await builder.waitForFields(["Full Name"]);

    await builder.switchToStep("Final");
    await builder.addField("Data");

    // New field renders as a card in the ACTIVE step's canvas
    await expect(
      page.locator('[data-form-builder-component="field-card"]')
    ).toHaveCount(2); // "Notes" + the new unlabeled Data field
    // And is NOT in step 2
    await builder.switchToStep("Contact");
    await expect(
      page.locator('[data-form-builder-component="field-card"]')
    ).toHaveCount(1); // only "Work Email"
  });
});
