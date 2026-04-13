import type { Page } from "@playwright/test";

export class FormBuilderPage {
  constructor(private page: Page) {}

  async goto(formId: string) {
    await this.page.goto(`/forms/edit-form/${formId}`);
  }

  async addField(fieldType: string) {
    // The sidebar defaults to "Add Fields" section
    await this.page.getByTestId(`field-type-${fieldType}`).hover();
    await this.page
      .getByTestId(`field-type-${fieldType}`)
      .getByRole("button")
      .click();
  }

  async save() {
    await this.page.getByTestId("btn-save-form").click();
    await this.page.waitForResponse(
      (r) => r.url().includes("/api/") && r.status() === 200
    );
  }

  async publish() {
    await this.page.getByTestId("btn-publish").click();
  }

  publishButton() {
    return this.page.getByTestId("btn-publish");
  }

  saveButton() {
    return this.page.getByTestId("btn-save-form");
  }
}
