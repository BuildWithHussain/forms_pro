import { useCall } from "frappe-ui";

/**
 * Check if login is required for a form submission page.
 *
 * @param route - The route of the form to check.
 *
 * @returns bool - True if login is required, False otherwise.
 */
export async function isLoginRequired(route: string) {
  const loginRequired = useCall({
    baseUrl: "/api/v2/method/",
    url: "forms_pro.api.form.is_login_required",
    params: { route },
    immediate: false,
  });

  await loginRequired.execute();
  return loginRequired.data;
}
