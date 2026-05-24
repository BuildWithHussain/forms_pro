import { test, expect } from "../fixtures/test-data.fixture";
import { SubmissionPage } from "../helpers/submission";

test.describe("Rating field", () => {
  test("retains the value the user clicked (no clamp to 1.0)", async ({
    browser,
    createPublishedForm,
    apiContext,
  }) => {
    const { formId, route } = await createPublishedForm();

    // Add a Rating field to the published form via REST
    const formRes = await apiContext.get(`/api/resource/Form/${formId}`);
    const { data: formData } = await formRes.json();
    const linkedDoctype: string = formData.linked_doctype;
    const ratingFieldname = "satisfaction";

    await apiContext.put(`/api/resource/Form/${formId}`, {
      data: {
        fields: [
          ...(formData.fields ?? []),
          {
            fieldtype: "Rating",
            label: "Satisfaction",
            fieldname: ratingFieldname,
            reqd: 0,
          },
        ],
      },
    });

    // Guest fills + submits the form
    const guestCtx = await browser.newContext();
    const guestPage = await guestCtx.newPage();
    const submissionPage = new SubmissionPage(guestPage);
    await submissionPage.goto(route);

    await expect(guestPage.getByRole("button", { name: "Submit" })).toBeVisible(
      { timeout: 10000 }
    );

    // Click the 3rd star (1-indexed → nth(2)). feather-icons stamps the class.
    const stars = guestPage.locator("svg.feather-star");
    await expect(stars).toHaveCount(5);
    await stars.nth(2).click();

    await submissionPage.submit();
    await expect(submissionPage.successMessage()).toBeVisible({
      timeout: 10000,
    });

    await guestCtx.close();

    // Fetch the submission record via REST and assert the stored value.
    // Frappe stores Rating as a 0..1 fraction → 3/5 == 0.6.
    const listRes = await apiContext.get(
      `/api/resource/${encodeURIComponent(linkedDoctype)}`,
      {
        params: {
          filters: JSON.stringify([["fp_linked_form", "=", formId]]),
          fields: JSON.stringify(["name"]),
          limit_page_length: 1,
        },
      }
    );
    const { data: list } = await listRes.json();
    expect(list).toHaveLength(1);
    const submissionName = list[0].name;

    const getRes = await apiContext.get(
      `/api/resource/${encodeURIComponent(linkedDoctype)}/${encodeURIComponent(
        submissionName
      )}`
    );
    const { data: submission } = await getRes.json();
    expect(submission[ratingFieldname]).toBeCloseTo(0.6, 5);
  });
});
