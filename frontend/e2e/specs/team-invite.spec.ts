import { test, expect } from "../fixtures/test-data.fixture";
import { TeamPage } from "../helpers/team";

test.describe("Team Management", () => {
  test("team page loads and shows Invite Member button", async ({ page }) => {
    const teamPage = new TeamPage(page);
    await teamPage.goto();
    await expect(
      page.getByRole("button", { name: /invite member/i })
    ).toBeVisible();
  });

  test("invite dialog opens with email input and send button", async ({
    page,
  }) => {
    const teamPage = new TeamPage(page);
    await teamPage.goto();
    await teamPage.openInviteDialog();

    const dialog = page.getByRole("dialog");
    await expect(dialog.getByLabel("Invite by Email")).toBeVisible();
    await expect(
      dialog.getByRole("button", { name: "Send Invitations" })
    ).toBeVisible();
  });

  test("team owner can invite a member by email", async ({ page }) => {
    const teamPage = new TeamPage(page);
    await teamPage.goto();
    await teamPage.openInviteDialog();
    await teamPage.inviteByEmail("testinvite@example.com");

    // Success toast appears
    await expect(page.getByText(/invitations sent successfully/i)).toBeVisible({
      timeout: 10000,
    });
  });
});
