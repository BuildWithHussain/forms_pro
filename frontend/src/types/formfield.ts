export { Fieldtype } from "@/types/FormsPro/form_field.types";
import { Fieldtype } from "@/types/FormsPro/form_field.types";

export type FormField = {
  label: string;
  fieldname: string;
  fieldtype: Fieldtype;
  description?: string;
  reqd?: boolean;
  hidden?: boolean;
  options?: string;
  default?: string;
  idx?: number;
  conditional_logic?: string;
  row_index?: number;
  column_index?: number;
};
