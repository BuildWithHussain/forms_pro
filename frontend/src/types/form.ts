import { FormField } from "./formfield";

export type Form = {
  name: string;
  title: string;
  description?: string;
  fields?: FormField[];
  route?: string;
  is_published?: boolean;
  allow_incomplete?: boolean;
  linked_doctype?: string;
  linked_team_id?: string;
  login_required?: boolean;
};
