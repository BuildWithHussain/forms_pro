import { test, expect } from "@playwright/test";

test("authenticated user can reach the forms dashboard", async ({ page }) => {
  const response = await page.goto("/forms");
  // Frappe dev server can 500 on the very first request under parallel test startup
  if (response?.status() === 500) {
    await page.reload({ waitUntil: "networkidle" });
  }
  await expect(page).not.toHaveURL(/login/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible({
    timeout: 15000,
  });
});
