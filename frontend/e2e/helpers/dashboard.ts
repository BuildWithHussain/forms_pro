import type { Page } from "@playwright/test";

export class DashboardPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/forms");
  }

  // Form title headings inside FormPreviewCard
  formTitles() {
    return this.page.getByRole("heading", { level: 3 });
  }
}
