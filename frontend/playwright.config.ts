import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e/specs",
  globalSetup: "./e2e/global-setup",
  outputDir: "./e2e/test-results",

  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:8001",
    storageState: "./e2e/auth/storageState.json",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  retries: 1,
  workers: process.env.CI ? 2 : undefined,

  reporter: [
    ["list"],
    ["html", { outputFolder: "./e2e/playwright-report", open: "never" }],
    ["github"],
  ],
});
