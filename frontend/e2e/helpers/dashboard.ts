import type { Page } from "@playwright/test";

export class DashboardPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/forms");
  }

  async clickNewForm() {
    await this.page.getByTestId("btn-new-form").click();
  }

  formCards() {
    return this.page.getByTestId("form-card");
  }
}
