import { test, expect } from "../fixtures/test-data.fixture";
import { SubmissionPage } from "../helpers/submission";

test.describe("Form Submission", () => {
  test("published form loads on the public submission page", async ({
    page,
    createPublishedForm,
  }) => {
    const { route } = await createPublishedForm();
    const submissionPage = new SubmissionPage(page);
    await submissionPage.goto(route);

    // The public form renders a Submit button (form is in filling state)
    await expect(page.getByRole("button", { name: "Submit" })).toBeVisible();
  });

  test("guest user can submit a published form", async ({
    browser,
    createPublishedForm,
  }) => {
    const { route } = await createPublishedForm();

    // Fresh context = no session cookies → simulates a real guest user
    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submissionPage = new SubmissionPage(guestPage);

    await submissionPage.goto(route);
    await expect(guestPage.getByRole("button", { name: "Submit" })).toBeVisible(
      { timeout: 10000 }
    );

    await submissionPage.submit();

    // Success section appears with the default thank-you copy
    await expect(submissionPage.successMessage()).toBeVisible({
      timeout: 10000,
    });

    await guestCtx.close();
  });
});
