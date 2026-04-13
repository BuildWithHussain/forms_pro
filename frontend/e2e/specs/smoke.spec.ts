import { test, expect } from "@playwright/test";

test("authenticated user can reach the forms dashboard", async ({ page }) => {
  await page.goto("/forms");
  // If auth works, we land on the dashboard (not the login page)
  await expect(page).not.toHaveURL(/login/);
  await expect(page.getByText("Dashboard")).toBeVisible();
});
