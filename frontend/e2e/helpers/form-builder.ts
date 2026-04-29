import type { Page } from "@playwright/test";

export class FormBuilderPage {
  constructor(private page: Page) {}

  async goto(
    formId: string,
    options?: { title?: string; skipTitleFill?: boolean }
  ) {
    await this.page.goto(`/forms/edit-form/${formId}`);
    // Wait for the sidebar to confirm the builder is mounted
    await this.page.waitForSelector(
      '[data-form-builder-component="form-builder-sidebar"]'
    );

    if (options?.skipTitleFill) return;

    // Set unique title to avoid MandatoryError on save (frontend transforms "Untitled Form" → "")
    const title = options?.title ?? `E2E Form ${Date.now()}`;
    await this.page.getByPlaceholder("Untitled Form").fill(title);

    // Save immediately so form is clean and Publish/Unpublish button shows
    const saveBtn = this.page.getByRole("button", {
      name: "Save",
      exact: true,
    });
    // Wait briefly for dirty state to propagate
    await this.page.waitForTimeout(200);
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
      await saveBtn.waitFor({ state: "hidden", timeout: 30000 });
    }
  }

  // Scope selectors to the sidebar (which has a stable pre-existing attribute)
  private sidebar() {
    return this.page.locator(
      '[data-form-builder-component="form-builder-sidebar"]'
    );
  }

  async addField(fieldType: string) {
    // Each card shows the field type name as visible text
    const card = this.sidebar()
      .getByText(fieldType, { exact: true })
      .locator("..");
    await card.hover();
    await card.getByRole("button").click();
  }

  // The canvas shows "Click on fields to add them…" when empty
  canvasEmptyState() {
    return this.page.getByText(/click on fields to add them/i);
  }

  async publish() {
    // After edits, form is dirty — header shows "Save" instead of "Publish".
    // Save first so the Publish button becomes available.
    const saveBtn = this.page.getByRole("button", {
      name: "Save",
      exact: true,
    });
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
      // Wait for Save to disappear — same render cycle as Publish appearing
      await saveBtn.waitFor({ state: "hidden", timeout: 30000 });
    }
    await this.page.getByRole("button", { name: /^publish$/i }).click();
    await this.page
      .getByRole("button", { name: /^unpublish$/i })
      .waitFor({ timeout: 10000 });
  }

  async unpublish() {
    await this.page.getByRole("button", { name: /^unpublish$/i }).click();
    await this.page
      .getByRole("button", { name: /^publish$/i })
      .waitFor({ timeout: 10000 });
  }

  publishButton() {
    return this.page.getByRole("button", { name: /^publish$/i });
  }
}
