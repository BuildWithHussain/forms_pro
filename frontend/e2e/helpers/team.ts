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
    await dialog.getByLabel("Invite by Email").fill(email);
    await dialog.getByLabel("Invite by Email").press("Enter");
    await dialog.getByRole("button", { name: "Send Invitations" }).click();
  }

  memberRows() {
    return this.page.getByRole("row");
  }
}
