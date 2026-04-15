import { test, expect } from "../fixtures/test-data.fixture";

test.describe("Submission Viewing", () => {
  test("submissions page shows empty state when no submissions exist", async ({
    page,
    createPublishedForm,
  }) => {
    const { formId } = await createPublishedForm();
    await page.goto(`/forms/manage/${formId}/submissions`);
    await expect(page.getByText("No Submissions Yet")).toBeVisible();
  });

  test("admin sees a submission row after a form is submitted", async ({
    page,
    createPublishedForm,
    submitForm,
  }) => {
    const { formId } = await createPublishedForm();
    await submitForm(formId);

    await page.goto(`/forms/manage/${formId}/submissions`);

    // Empty state should be gone; the "Submitted" badge appears in a row
    await expect(page.getByText("No Submissions Yet")).not.toBeVisible();
    await expect(page.getByText("Submitted").first()).toBeVisible({
      timeout: 10000,
    });
  });
});
