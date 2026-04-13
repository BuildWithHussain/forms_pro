import type { Page } from "@playwright/test";

export class SubmissionPage {
  constructor(private page: Page) {}

  async goto(route: string) {
    await this.page.goto(`/forms/p/${route}`);
  }

  async fillField(label: string, value: string) {
    await this.page.getByLabel(label).fill(value);
  }

  async submit() {
    await this.page.getByRole("button", { name: "Submit" }).click();
  }

  // After successful submission the SuccessSection renders; detect via its description text
  successMessage() {
    return this.page.getByText(/thank you for submitting/i);
  }
}
