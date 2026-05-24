import { test, expect } from "../fixtures/test-data.fixture";

test.describe("Route-level permissions", () => {
  test("bogus form id renders Not Found and surfaces 404", async ({ page }) => {
    const responsePromise = page.waitForResponse(
      (res) =>
        res
          .url()
          .includes("/api/method/forms_pro.api.form.get_form_for_view") &&
        res.status() === 404,
      { timeout: 15000 }
    );

    await page.goto("/forms/manage/MISSING-FORM-XYZ-E2E");

    const response = await responsePromise;
    expect(response.status()).toBe(404);

    await expect(page.getByRole("heading", { name: /not found/i })).toBeVisible(
      { timeout: 10000 }
    );
  });

  test("owner navigates to edit-form and the builder renders", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();

    const responsePromise = page.waitForResponse(
      (res) =>
        res
          .url()
          .includes("/api/method/forms_pro.api.form.get_form_for_edit") &&
        res.status() === 200,
      { timeout: 15000 }
    );

    await page.goto(`/forms/edit-form/${formId}`);

    const response = await responsePromise;
    expect(response.status()).toBe(200);

    // RouteError must not render for an authorized owner.
    await expect(
      page.getByRole("heading", { name: /access denied|not found/i })
    ).toHaveCount(0);
  });

  // Deferred: read-only viewer hitting /edit-form/:id should see "Access Denied"
  // plus a 403 in the network. Reliable setup needs an admin-owned form shared
  // read-only with the test user, which requires a second authenticated API
  // context (admin login) that the current fixture does not provide. Add when
  // we wire an admin fixture into e2e/global-setup.
});
