import { test, expect } from "../fixtures/test-data.fixture";
import { SubmissionPage } from "../helpers/submission";
import {
  setFormFields,
  threeStepFields,
  pageBreak,
} from "../helpers/form-fields";

test.describe("Multi-step public submission", () => {
  test("renders stepper with labels, counts, and only first step's fields", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const sub = new SubmissionPage(page);
    await sub.goto(route);

    await expect(sub.stepIndicator()).toBeVisible();
    await expect(sub.stepNode(0)).toContainText("Basics");
    await expect(sub.stepNode(1)).toContainText("Contact");
    await expect(sub.stepNode(2)).toContainText("Final");
    await expect(sub.stepNode(0)).toContainText("1 field");

    await expect(sub.fieldInput("Full Name")).toBeVisible();
    await expect(sub.fieldInput("Work Email")).toHaveCount(0);
  });

  test("back hidden on first step, submit only on last step", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await expect(sub.backButton()).toHaveCount(0);
    await expect(sub.submitButton()).toHaveCount(0);
    await expect(sub.nextButton()).toBeVisible();

    await sub.next();
    await expect(sub.backButton()).toBeVisible();
    await expect(sub.nextButton()).toBeVisible();
    await expect(sub.submitButton()).toHaveCount(0);

    await sub.next();
    await expect(sub.submitButton()).toBeVisible();
    await expect(sub.nextButton()).toHaveCount(0);
  });

  test("values survive next/back navigation", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await sub.fillField("Full Name", "Ada Lovelace");
    await sub.next();
    await sub.fillField("Work Email", "ada@example.com");
    await sub.back();

    await expect(sub.fieldInput("Full Name")).toHaveValue("Ada Lovelace");
    await sub.next();
    await expect(sub.fieldInput("Work Email")).toHaveValue("ada@example.com");
  });

  test("step indicator marks done/current/todo and allows click-back", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await expect(sub.stepNode(0)).toHaveAttribute("data-step-state", "current");
    await expect(sub.stepNode(1)).toHaveAttribute("data-step-state", "todo");

    await sub.next();
    await expect(sub.stepNode(0)).toHaveAttribute("data-step-state", "done");
    await expect(sub.stepNode(1)).toHaveAttribute("data-step-state", "current");

    // Completed steps are clickable
    await sub.stepNode(0).click();
    await expect(sub.fieldInput("Full Name")).toBeVisible();
    await expect(sub.stepNode(0)).toHaveAttribute("data-step-state", "current");

    // Future steps are NOT clickable
    await sub.stepNode(2).click();
    await expect(sub.stepNode(0)).toHaveAttribute("data-step-state", "current");
  });

  test("full multi-step submission writes all values to the linked document", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await sub.fillField("Full Name", "Grace Hopper");
    await sub.next();
    await sub.fillField("Work Email", "grace@example.com");
    await sub.next();
    await sub.fillField("Notes", "multi step works");
    await sub.submit();
    await expect(sub.successMessage()).toBeVisible({ timeout: 15000 });

    // Resolve linked doctype, then fetch the submission document
    const formRes = await apiContext.get(`/api/resource/Form/${formId}`);
    const linkedDoctype = (await formRes.json()).data.linked_doctype as string;
    const filters = encodeURIComponent(
      JSON.stringify([["fp_linked_form", "=", formId]])
    );
    const fields = encodeURIComponent(
      JSON.stringify(["name", "full_name", "work_email", "notes"])
    );
    const listRes = await apiContext.get(
      `/api/resource/${encodeURIComponent(
        linkedDoctype
      )}?filters=${filters}&fields=${fields}`
    );
    const docs = (await listRes.json()).data as Array<Record<string, string>>;
    expect(docs).toHaveLength(1);
    expect(docs[0].full_name).toBe("Grace Hopper");
    expect(docs[0].work_email).toBe("grace@example.com");
    expect(docs[0].notes).toBe("multi step works");
  });

  test("single-step form renders without stepper and submits directly", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, [{ label: "Only Field" }]);
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Only Field")).toBeVisible();

    await expect(sub.stepNode(0)).toHaveCount(0);
    await expect(sub.nextButton()).toHaveCount(0);
    await expect(sub.submitButton()).toBeVisible();
  });

  // Frappe rejects Page Break rows with an empty label via REST (MandatoryError),
  // so this layout can't be API-seeded today. Flip to test() if seeding is fixed.
  test.fixme(
    "unlabeled page breaks render numbered steps without labels",
    async ({ page, createPublishedForm, apiContext }) => {
      const { route, formId } = await createPublishedForm();
      await setFormFields(apiContext, formId, [
        { label: "Alpha" },
        pageBreak("", "pb_1"),
        { label: "Beta" },
      ]);
      const sub = new SubmissionPage(page);
      await sub.goto(route);
      await expect(sub.fieldInput("Alpha")).toBeVisible();

      // Two numbered nodes, neither carrying a stale label
      await expect(sub.stepNode(0)).toContainText("1");
      await expect(sub.stepNode(1)).toContainText("2");
      await expect(sub.stepNode(0)).not.toContainText("Step");
    }
  );

  test("guest can complete a multi-step submission", async ({
    browser,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());

    const guestContext = await browser.newContext({
      storageState: { cookies: [], origins: [] },
    });
    const guestPage = await guestContext.newPage();
    const sub = new SubmissionPage(guestPage);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await sub.fillField("Full Name", "Guest User");
    await sub.next();
    await sub.fillField("Work Email", "guest@example.com");
    await sub.next();
    await sub.fillField("Notes", "from guest");
    await sub.submit();
    await expect(sub.successMessage()).toBeVisible({ timeout: 15000 });

    await guestContext.close();
  });

  test("conditional field on a later step reacts to value from an earlier step", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, [
      pageBreak("Basics", "pb_basics"),
      {
        label: "Trigger",
        conditional_logic: JSON.stringify({
          conditions: [{ fieldname: "trigger", operator: "Is", value: "yes" }],
          action: "Show Field",
          target_field: "bonus",
        }),
      },
      pageBreak("Extras", "pb_extras"),
      { label: "Bonus", hidden: 1 },
    ]);
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Trigger")).toBeVisible();

    // Condition not met -> Bonus hidden on step 2
    await sub.next();
    await expect(sub.fieldInput("Bonus")).toHaveCount(0);

    // Meet the condition on step 1 -> Bonus appears on step 2
    await sub.back();
    await sub.fillField("Trigger", "yes");
    await sub.next();
    await expect(sub.fieldInput("Bonus")).toBeVisible();
  });

  test("stepper stays visible and usable on a small viewport", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());
    await page.setViewportSize({ width: 375, height: 700 });
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();

    await expect(sub.stepIndicator()).toBeVisible();
    await sub.next();
    await expect(sub.stepNode(1)).toHaveAttribute("data-step-state", "current");
    await expect(sub.fieldInput("Work Email")).toBeVisible();
  });

  // Behavior pin: the public edit page has no step support today; it renders
  // all fields flat. If steps are added there later, replace this test.
  test("edit-submission page renders all multi-step fields flat", async ({
    page,
    createPublishedForm,
    apiContext,
  }) => {
    const { route, formId } = await createPublishedForm();
    await setFormFields(apiContext, formId, threeStepFields());

    // Create a submission as the logged-in user via the UI (simplest reliable path)
    const sub = new SubmissionPage(page);
    await sub.goto(route);
    await expect(sub.fieldInput("Full Name")).toBeVisible();
    await sub.fillField("Full Name", "Edit Me");
    await sub.next();
    await sub.fillField("Work Email", "edit@example.com");
    await sub.next();
    await sub.fillField("Notes", "before edit");
    await sub.submit();
    await expect(sub.successMessage()).toBeVisible({ timeout: 15000 });

    // Find the submission document name
    const formRes = await apiContext.get(`/api/resource/Form/${formId}`);
    const linkedDoctype = (await formRes.json()).data.linked_doctype as string;
    const filters = encodeURIComponent(
      JSON.stringify([["fp_linked_form", "=", formId]])
    );
    const listRes = await apiContext.get(
      `/api/resource/${encodeURIComponent(linkedDoctype)}?filters=${filters}`
    );
    const submissionName = (await listRes.json()).data[0].name as string;

    await page.goto(`/forms/p/${route}/edit/${submissionName}`);
    // PublicEdit uses FormRenderer without StepIndicator but still filters to
    // currentStepFields — only step 0 renders; custom actions replace Next/Back.
    await expect(sub.fieldInput("Full Name")).toBeVisible();
    await expect(sub.fieldInput("Work Email")).toHaveCount(0);
    await expect(sub.fieldInput("Notes")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Next" })).toHaveCount(0);
  });
});
