import type { Page } from "@playwright/test";

export class TeamPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/forms/team");
    // Wait for the API calls (team members, etc.) to complete before proceeding
    await this.page.waitForLoadState("networkidle");
  }

  async openInviteDialog() {
    await this.page.getByRole("button", { name: /invite member/i }).click();
    // Wait until the dialog's email input is interactive, not just the dialog shell
    await this.page
      .getByRole("dialog")
      .getByLabel("Invite by Email")
      .waitFor({ state: "visible" });
  }

  async inviteByEmail(email: string) {
    const dialog = this.page.getByRole("dialog");
    await dialog.getByLabel("Invite by Email").fill(email);
    // Click "Add" to move the email into the pending invites list
    await dialog.getByRole("button", { name: "Add" }).click();
    await dialog.getByRole("button", { name: "Send Invitations" }).click();
  }

  memberRows() {
    return this.page.getByRole("row");
  }
}
