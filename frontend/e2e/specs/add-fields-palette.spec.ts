import { test, expect } from "../fixtures/test-data.fixture";
import { FormBuilderPage } from "../helpers/form-builder";

test.describe("Add Fields palette", () => {
  test("renders palette items as buttons without live input previews", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    const sidebar = page.locator(
      '[data-form-builder-component="form-builder-sidebar"]'
    );

    // Palette items are buttons, named after the fieldtype
    await expect(
      sidebar.getByRole("button", { name: "Data", exact: true })
    ).toBeVisible();
    await expect(
      sidebar.getByRole("button", { name: "Email", exact: true })
    ).toBeVisible();
    await expect(
      sidebar.getByRole("button", { name: "Phone", exact: true })
    ).toBeVisible();

    // No autofillable inputs inside palette buttons (regression: previously
    // each palette card mounted a live FormControl, which triggered browser
    // autofill on type=email / type=tel / type=password).
    const emailBtn = sidebar.getByRole("button", {
      name: "Email",
      exact: true,
    });
    await expect(emailBtn.locator("input")).toHaveCount(0);

    const phoneBtn = sidebar.getByRole("button", {
      name: "Phone",
      exact: true,
    });
    await expect(phoneBtn.locator("input")).toHaveCount(0);
  });

  test("search filters palette items", async ({ page, createForm }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    const sidebar = page.locator(
      '[data-form-builder-component="form-builder-sidebar"]'
    );

    await expect(
      sidebar.getByRole("button", { name: "Data", exact: true })
    ).toBeVisible();
    await expect(
      sidebar.getByRole("button", { name: "Phone", exact: true })
    ).toBeVisible();

    await sidebar.getByPlaceholder("Search Fields").fill("date");

    // "Date", "Date Time", "Date Range" remain (case-insensitive substring)
    await expect(
      sidebar.getByRole("button", { name: "Date", exact: true })
    ).toBeVisible();
    // Unrelated types are filtered out
    await expect(
      sidebar.getByRole("button", { name: "Phone", exact: true })
    ).toHaveCount(0);
    await expect(
      sidebar.getByRole("button", { name: "Data", exact: true })
    ).toHaveCount(0);
  });

  test("clicking a palette item adds the field to the canvas", async ({
    page,
    createForm,
  }) => {
    const formId = await createForm();
    const builder = new FormBuilderPage(page);
    await builder.goto(formId);

    await expect(builder.canvasEmptyState()).toBeVisible();
    await builder.addField("Email");
    await expect(builder.canvasEmptyState()).not.toBeVisible();
  });
});
