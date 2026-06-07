import {
  FIELD_TYPE_DEFINITIONS,
  FIELD_TYPE_MAP,
  getFieldTypeDef,
} from "@/config/fieldTypes";
import type { FieldTypeDefinition } from "@/config/fieldTypes";
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import type { Component } from "vue";

// Re-export the registry under the names the rest of the codebase uses
export {
  FIELD_TYPE_DEFINITIONS as formFields,
  getFieldTypeDef,
  FIELD_TYPE_MAP,
};
export type { FieldTypeDefinition as FormFields };

// Subset type used by RenderField.vue
export type FormFieldType = {
  component: Component;
  props: Record<string, unknown>;
};

// Maps Frappe DocType fieldtypes to the equivalent Forms Pro fieldtype.
// Used when importing fields from an existing DocType into a form.
export const mapDoctypeFieldForForm = (
  fieldtype: string
): string | undefined => {
  const FRAPPE_TO_FORM_TYPE: Partial<Record<string, Fieldtype>> = {
    Autocomplete: Fieldtype.DATA,
    Attach: Fieldtype.ATTACH,
    "Attach Image": Fieldtype.ATTACH,
    Check: Fieldtype.CHECKBOX,
    Currency: Fieldtype.NUMBER,
    Data: Fieldtype.DATA,
    Date: Fieldtype.DATE,
    Datetime: Fieldtype.DATE_TIME,
    Float: Fieldtype.NUMBER,
    "HTML Editor": Fieldtype.TEXT_EDITOR,
    Int: Fieldtype.NUMBER,
    Link: Fieldtype.LINK,
    "Long Text": Fieldtype.TEXTAREA,
    "Markdown Editor": Fieldtype.TEXT_EDITOR,
    Password: Fieldtype.PASSWORD,
    Percent: Fieldtype.NUMBER,
    Phone: Fieldtype.PHONE,
    Rating: Fieldtype.RATING,
    Select: Fieldtype.SELECT,
    "Small Text": Fieldtype.TEXTAREA,
    Table: Fieldtype.TABLE,
    Text: Fieldtype.TEXTAREA,
    "Text Editor": Fieldtype.TEXT_EDITOR,
    Time: Fieldtype.TIME_PICKER,
  };

  return FRAPPE_TO_FORM_TYPE[fieldtype];
};

export const isHeading = (fieldtype: Fieldtype): boolean => {
  return [
    Fieldtype.HEADING_1,
    Fieldtype.HEADING_2,
    Fieldtype.HEADING_3,
  ].includes(fieldtype);
};

export const isPageBreak = (fieldtype: Fieldtype): boolean => {
  return fieldtype === Fieldtype.PAGE_BREAK;
};

export const isDisplayOnly = (fieldtype: Fieldtype): boolean => {
  return isHeading(fieldtype) || isPageBreak(fieldtype);
};
