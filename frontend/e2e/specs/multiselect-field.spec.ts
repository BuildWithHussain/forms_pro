import { test, expect } from "../fixtures/test-data.fixture";
import { FormBuilderPage } from "../helpers/form-builder";
import { SubmissionPage } from "../helpers/submission";

test.describe("Multiselect field", () => {
  test("add options in builder, publish, submit via public form", async ({
    page,
    browser,
    createForm,
    apiContext,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    // Set a form title so Save doesn't fail with MandatoryError (title is required)
    await page.getByPlaceholder("Untitled Form").fill("Multiselect Test Form");

    // Add Multiselect field from sidebar; wait for canvas extras to confirm render
    await builder.addField("Multiselect");
    await expect(page.getByRole("button", { name: "Add Option" })).toBeVisible({
      timeout: 10000,
    });

    // Set a label
    await page.getByPlaceholder("Label").fill("Favourite Colors");

    // Add three options via the builder extras button
    const options = ["Option A", "Option B", "Option C"];
    for (const option of options) {
      await expect(
        page.getByRole("button", { name: "Add Option" })
      ).toBeVisible({ timeout: 5000 });
      await page.getByRole("button", { name: "Add Option" }).click();
      await page.getByPlaceholder("Type option and press Enter").fill(option);
      await page.keyboard.press("Enter");
    }

    // Publish — assert no error toast appears
    await builder.publish();
    await expect(
      page.locator("[data-sonner-toast][data-type='error']")
    ).not.toBeVisible();

    // Fetch the public route
    const res = await apiContext.get(`/api/resource/Form/${formId}`);
    const { data } = await res.json();
    const route: string = data.route;

    // Open as guest
    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submissionPage = new SubmissionPage(guestPage);

    await submissionPage.goto(route);
    await expect(guestPage.getByRole("button", { name: "Submit" })).toBeVisible(
      { timeout: 10000 }
    );

    // Select two options
    await guestPage.locator("label", { hasText: "Option A" }).click();
    await guestPage.locator("label", { hasText: "Option B" }).click();

    await submissionPage.submit();

    await expect(submissionPage.successMessage()).toBeVisible({
      timeout: 10000,
    });

    await guestCtx.close();
  });
});
