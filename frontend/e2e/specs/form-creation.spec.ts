import { test, expect } from "../fixtures/test-data.fixture";
import { DashboardPage } from "../helpers/dashboard";
import { FormBuilderPage } from "../helpers/form-builder";

test.describe("Form Creation", () => {
  test("form title appears on dashboard after creation via API", async ({
    page,
    createForm,
  }) => {
    await createForm();
    const dashboard = new DashboardPage(page);
    await dashboard.goto();
    await expect(dashboard.formTitles().first()).toBeVisible();
  });

  test("form builder loads and shows Add Fields sidebar", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);
    await expect(page.getByText("Add Fields")).toBeVisible();
    await expect(page.getByText("Data", { exact: true }).first()).toBeVisible();
  });

  test("adding a field removes the canvas empty state", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    await expect(builder.canvasEmptyState()).toBeVisible();
    await builder.addField("Data");
    await expect(builder.canvasEmptyState()).not.toBeVisible();
  });

  test("can publish a draft form", async ({ page, createForm }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    // Fresh form is a draft → Publish button visible
    await expect(builder.publishButton()).toBeVisible();
    await builder.publish();

    // After publishing, button flips to Unpublish
    await expect(
      page.getByRole("button", { name: /^unpublish$/i })
    ).toBeVisible();
  });

  test("can unpublish a published form", async ({
    page,
    createPublishedForm,
  }) => {
    const { formId } = await createPublishedForm();
    const builder = new FormBuilderPage(page);
    // skipTitleFill: createPublishedForm already set title, don't make form dirty
    await builder.goto(formId, { skipTitleFill: true });

    // Published form → Unpublish button visible
    await expect(
      page.getByRole("button", { name: /^unpublish$/i })
    ).toBeVisible();
    await builder.unpublish();

    await expect(builder.publishButton()).toBeVisible();
  });
});
