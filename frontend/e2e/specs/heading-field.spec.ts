import { test, expect } from "../fixtures/test-data.fixture";
import { FormBuilderPage } from "../helpers/form-builder";
import { SubmissionPage } from "../helpers/submission";

test.describe("Heading fields", () => {
  test("all three heading types appear in the Add Fields sidebar", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    const sidebar = page.locator(
      '[data-form-builder-component="form-builder-sidebar"]'
    );
    await expect(sidebar.getByText("Heading 1", { exact: true })).toBeVisible();
    await expect(sidebar.getByText("Heading 2", { exact: true })).toBeVisible();
    await expect(sidebar.getByText("Heading 3", { exact: true })).toBeVisible();
  });

  test("adding Heading 1 shows editable input in builder (edit mode)", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    await builder.addField("Heading 1");

    // In edit mode (field selected), shows input with placeholder
    const headingInput = page.getByPlaceholder("Heading Text").first();
    await expect(headingInput).toBeVisible({ timeout: 5000 });
  });

  test("heading label is editable in builder", async ({ page, createForm }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    await builder.addField("Heading 1");

    // Edit mode shows a text input for the heading label
    const headingInput = page.getByPlaceholder("Heading Text").first();
    await expect(headingInput).toBeVisible({ timeout: 5000 });
    await headingInput.fill("About You");

    // Verify the input has the value we typed
    await expect(headingInput).toHaveValue("About You");
  });

  test("heading renders on the public submission page without an input", async ({
    page,
    browser,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    await builder.addField("Heading 2");
    const headingInput = page.getByPlaceholder("Heading Text").first();
    await expect(headingInput).toBeVisible({ timeout: 5000 });
    await headingInput.fill("Your Details");

    await builder.publish();

    const res = await apiContext.get(`/api/resource/Form/${formId}`);
    const { data } = await res.json();
    const route: string = data.route;

    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submissionPage = new SubmissionPage(guestPage);
    await submissionPage.goto(route);

    // Heading renders as text, not as an input
    await expect(
      guestPage.locator("h3", { hasText: "Your Details" })
    ).toBeVisible({
      timeout: 10000,
    });
    // h3 because Heading 2 → h3 tag in Heading.vue

    await guestCtx.close();
  });

  test("form with heading fields submits successfully", async ({
    browser,
    createPublishedForm,
    apiContext,
  }) => {
    const { formId, route } = await createPublishedForm();

    // Add a Heading 1 field to the published form via REST
    const formRes = await apiContext.get(`/api/resource/Form/${formId}`);
    const { data: formData } = await formRes.json();

    await apiContext.put(`/api/resource/Form/${formId}`, {
      data: {
        fields: [
          ...(formData.fields ?? []),
          {
            fieldtype: "Heading 1",
            label: "Section Header",
            fieldname: "section_header",
            reqd: 0,
          },
        ],
      },
    });

    // Guest submits — heading must not cause a server-side validation error
    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submissionPage = new SubmissionPage(guestPage);
    await submissionPage.goto(route);

    await expect(guestPage.getByRole("button", { name: "Submit" })).toBeVisible(
      {
        timeout: 10000,
      }
    );
    await submissionPage.submit();

    await expect(submissionPage.successMessage()).toBeVisible({
      timeout: 10000,
    });

    await guestCtx.close();
  });
});
