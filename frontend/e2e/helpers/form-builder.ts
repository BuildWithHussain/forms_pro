import type { Page } from "@playwright/test";

export class FormBuilderPage {
  constructor(private page: Page) {}

  async goto(formId: string) {
    await this.page.goto(`/forms/edit-form/${formId}`);
    // Wait for the sidebar to confirm the builder is mounted
    await this.page.waitForSelector(
      '[data-form-builder-component="form-builder-sidebar"]'
    );
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
    // Click Publish and wait for the label to flip to "Unpublish"
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
