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
    await this.page.getByTestId("btn-submit-form").click();
  }

  successSection() {
    return this.page.getByTestId("submission-success");
  }
}
