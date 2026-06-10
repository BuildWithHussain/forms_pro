import type { Locator, Page } from "@playwright/test";

export class SubmissionPage {
  constructor(private page: Page) {}

  async goto(route: string) {
    await this.page.goto(`/forms/p/${route}`);
  }

  // Submission fields render a visible <label> sibling, not a for/id association.
  fieldInput(label: string): Locator {
    return this.page
      .locator("div.flex.flex-col.gap-2")
      .filter({ has: this.page.getByText(label, { exact: true }) })
      .getByRole("textbox");
  }

  async fillField(label: string, value: string) {
    await this.fieldInput(label).fill(value);
  }

  async submit() {
    await this.page.getByRole("button", { name: "Submit" }).click();
  }

  // After successful submission the SuccessSection renders; detect via its description text
  successMessage() {
    return this.page.getByText(/thank you for submitting/i);
  }

  // ---- Multi-step navigation ----

  stepIndicator(): Locator {
    return this.page.locator('nav[aria-label="Form steps"]');
  }

  stepNode(index: number): Locator {
    return this.page.locator(
      `[data-step-component="step-node"][data-step-index="${index}"]`
    );
  }

  nextButton(): Locator {
    return this.page.getByRole("button", { name: "Next" });
  }

  backButton(): Locator {
    return this.page.getByRole("button", { name: "Back" });
  }

  submitButton(): Locator {
    return this.page.getByRole("button", { name: "Submit" });
  }

  async next() {
    await this.nextButton().click();
  }

  async back() {
    await this.backButton().click();
  }
}
