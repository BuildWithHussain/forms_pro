import { chromium, type FullConfig } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const AUTH_FILE = path.join(__dirname, "auth/storageState.json");

export default async function globalSetup(_config: FullConfig) {
  fs.mkdirSync(path.dirname(AUTH_FILE), { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const baseURL = process.env.BASE_URL ?? "http://localhost:8001";

  await page.goto(baseURL);
  await page.request.post(`${baseURL}/api/method/login`, {
    form: {
      usr: process.env.TEST_USER_EMAIL ?? "test_forms_pro_user@example.com",
      pwd: process.env.TEST_USER_PASSWORD ?? "testforms123",
    },
  });

  await context.storageState({ path: AUTH_FILE });
  await browser.close();
}
