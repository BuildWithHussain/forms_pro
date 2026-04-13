import type { Page } from "@playwright/test";

export class TeamPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/forms/team");
  }

  async openInviteDialog() {
    await this.page.getByRole("button", { name: /invite member/i }).click();
  }

  async inviteByEmail(email: string) {
    const dialog = this.page.getByRole("dialog");
    // frappe-ui FormControl renders a wrapper div; target the inner input
    await dialog.getByTestId("input-invite-email").locator("input").fill(email);
    // Press Enter to add the email to the list
    await dialog
      .getByTestId("input-invite-email")
      .locator("input")
      .press("Enter");
    await dialog.getByTestId("btn-send-invite").click();
  }

  memberRows() {
    return this.page.getByRole("row");
  }
}
