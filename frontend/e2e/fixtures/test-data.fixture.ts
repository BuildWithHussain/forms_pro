import {
  test as base,
  request,
  type APIRequestContext,
} from "@playwright/test";

type TestDataFixtures = {
  apiContext: APIRequestContext;
  getTeamId: () => Promise<string>;
  createForm: () => Promise<string>;
  createPublishedForm: () => Promise<{ formId: string; route: string }>;
  submitForm: (formId: string) => Promise<void>;
};

async function fetchTeamId(apiContext: APIRequestContext): Promise<string> {
  const res = await apiContext.get(
    "/api/method/forms_pro.api.user.get_user_teams"
  );
  const { message } = await res.json();
  if (!message?.length) throw new Error("No team found for test user");
  return message[0].name as string;
}

export const test = base.extend<TestDataFixtures>({
  apiContext: async ({}, use) => {
    const ctx = await request.newContext({
      baseURL: process.env.BASE_URL ?? "http://localhost:8001",
      storageState: "./e2e/auth/storageState.json",
    });
    await use(ctx);
    await ctx.dispose();
  },

  getTeamId: async ({ apiContext }, use) => {
    await use(() => fetchTeamId(apiContext));
  },

  createForm: async ({ apiContext }, use) => {
    const created: string[] = [];

    await use(async () => {
      const teamId = await fetchTeamId(apiContext);
      const res = await apiContext.post(
        "/api/method/forms_pro.utils.form_generator.create_form",
        { data: { team_id: teamId } }
      );
      const { message } = await res.json();
      const formId = message.form_document as string;
      created.push(formId);
      return formId;
    });

    // Teardown: delete all created forms
    for (const id of created) {
      await apiContext.delete(`/api/resource/Form/${id}`).catch(() => {});
    }
  },

  createPublishedForm: async ({ apiContext }, use) => {
    const created: string[] = [];

    await use(async () => {
      const teamId = await fetchTeamId(apiContext);
      const createRes = await apiContext.post(
        "/api/method/forms_pro.utils.form_generator.create_form",
        { data: { team_id: teamId } }
      );
      const { message } = await createRes.json();
      const formId = message.form_document as string;
      created.push(formId);

      // Publish the form via Frappe REST API (also set title to avoid "Untitled Form" transform)
      const publishRes = await apiContext.put(`/api/resource/Form/${formId}`, {
        data: { is_published: 1, title: `E2E Published Form ${Date.now()}` },
      });
      const publishData = await publishRes.json();
      const route = publishData.data?.route as string;

      return { formId, route };
    });

    for (const id of created) {
      await apiContext.delete(`/api/resource/Form/${id}`).catch(() => {});
    }
  },

  // Creates a guest submission against an already-published form
  submitForm: async ({ apiContext }, use) => {
    await use(async (formId: string) => {
      await apiContext.post(
        "/api/method/forms_pro.api.submission.submit_form_response",
        { data: { form_id: formId, form_data: [] } }
      );
    });
  },
});

export { expect } from "@playwright/test";
