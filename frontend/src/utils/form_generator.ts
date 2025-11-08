import { createResource } from "frappe-ui";

export const createNewFormWithDoctype = async (linked_doctype: string, category: string | null = null) => {
  const form = createResource({
    url: "forms_pro.utils.form_generator.create_form_with_doctype",
    makeParams() {
      return {
        doctype: linked_doctype,
        category: category || null,
      };
    },
  });

  await form.fetch();
  return form.data;
};

export const createNewForm = async (category: string | null = null) => {
  const form = createResource({
    url: "forms_pro.utils.form_generator.create_form",
    makeParams() {
      return {
        category: category || null,
      };
    },
  });

  await form.fetch();
  return form.data;
};

export const validateFormRoute = async (
  curr_form_id: string,
  route: string,
) => {
  const route_exists = createResource({
    url: "frappe.client.get_count",
    makeParams() {
      return {
        doctype: "Form",
        filters: {
          name: ["!=", curr_form_id],
          route: route,
        },
      };
    },
  });

  await route_exists.fetch();
  return route_exists.data > 0;
};
