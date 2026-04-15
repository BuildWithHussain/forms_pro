/**
 * SINGLE SOURCE OF TRUTH for field type metadata.
 *
 * Every property that varies by field type — Vue component, layout behaviour,
 * Frappe fieldtype mapping, boolean/date semantics — lives here. Nothing else
 * in the frontend should hardcode field-type-specific logic; import from this
 * file and derive from the registry instead.
 *
 * The `Fieldtype` enum itself is auto-generated from `form_field.json` via
 * frappe-types, so the JSON is the ground truth for the list of valid names.
 * This registry owns everything that can't be auto-generated.
 *
 * To add a new field type:
 *   1. Add the option to `form_field.json`
 *      → `DF.Literal` (Python) and `Fieldtype` (TS) regenerate automatically.
 *   2. TypeScript will error in FIELD_TYPE_DEFINITIONS below until you add an entry.
 *   3. Add a matching entry to `FORM_TO_FRAPPE_FIELDTYPE` in `form_field.py`.
 *   4. Create a Vue component if the type needs a new input widget.
 */

import type { Component } from "vue";
import {
  Checkbox,
  DatePicker,
  DateRangePicker,
  DateTimePicker,
  Password,
  Rating,
  Select,
  Switch,
  Textarea,
  TextEditor,
  TimePicker,
  FormControl,
} from "frappe-ui";
import Attachment from "@/components/fields/Attachment.vue";
import Multiselect from "@/components/fields/Multiselect.vue";
import Phone from "@/components/fields/Phone.vue";
import Table from "@/components/fields/Table.vue";
import { Fieldtype } from "@/types/FormsPro/form_field.types";

export { Fieldtype };

/**
 * Controls how FieldRenderer positions the label relative to the input widget.
 *
 * - "default"           label on top, input below, description at the bottom
 * - "inline"            input first, label to the right (Switch, Checkbox)
 * - "description-first" label on top, description below label, input at the bottom (Text Editor)
 * - "custom"            the component handles its own full layout (Table)
 */
export type FieldLayout = "default" | "inline" | "description-first" | "custom";

export type FieldTypeDefinition = {
  /** Canonical name — must match a Fieldtype enum value */
  name: Fieldtype;
  /** Vue component used to render this field in input mode */
  component: Component;
  /** Default props forwarded to the component */
  props: Record<string, unknown>;
  /** How FieldRenderer lays out the label relative to the input */
  layout: FieldLayout;
  /** Frappe fieldtype to use when syncing this field to a DocType */
  frappeFieldtype: string;
  /** Override the `options` value on the Frappe CustomField (e.g. "Email" for Data fields) */
  frappeOptions?: string;
  /** True for Switch / Checkbox — affects conditional logic evaluation and display */
  isBoolean: boolean;
  /** True for Date / DateTime / DateRange / TimePicker — affects display formatting */
  isDate: boolean;
};

export const FIELD_TYPE_DEFINITIONS: FieldTypeDefinition[] = [
  {
    name: Fieldtype.ATTACH,
    component: Attachment,
    props: {
      variant: "outline",
      filetypes: ["image/*", ".jpg", ".gif", ".pdf"],
    },
    layout: "custom",
    frappeFieldtype: "Attach",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.DATA,
    component: FormControl,
    props: { type: "text", variant: "outline" },
    layout: "default",
    frappeFieldtype: "Data",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.NUMBER,
    component: FormControl,
    props: { type: "number", variant: "outline" },
    layout: "default",
    frappeFieldtype: "Int",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.EMAIL,
    component: FormControl,
    props: { type: "email", variant: "outline" },
    layout: "default",
    frappeFieldtype: "Data",
    frappeOptions: "Email",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.DATE,
    component: DatePicker,
    props: { variant: "outline", clearable: true, format: "D MMM YYYY" },
    layout: "default",
    frappeFieldtype: "Date",
    isBoolean: false,
    isDate: true,
  },
  {
    name: Fieldtype.DATE_TIME,
    component: DateTimePicker,
    props: {
      format: "DD MMM YYYY, hh:mm A",
      clearable: true,
      variant: "outline",
    },
    layout: "default",
    frappeFieldtype: "Datetime",
    isBoolean: false,
    isDate: true,
  },
  {
    name: Fieldtype.DATE_RANGE,
    component: DateRangePicker,
    props: { clearable: true, variant: "outline", format: "DD MMM 'YY" },
    layout: "default",
    frappeFieldtype: "Data",
    isBoolean: false,
    isDate: true,
  },
  {
    name: Fieldtype.TIME_PICKER,
    component: TimePicker,
    props: { variant: "outline", use12Hour: true, clearable: true },
    layout: "default",
    frappeFieldtype: "Time",
    isBoolean: false,
    isDate: true,
  },
  {
    name: Fieldtype.PASSWORD,
    component: Password,
    props: { variant: "outline" },
    layout: "default",
    frappeFieldtype: "Password",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.SELECT,
    component: Select,
    props: { variant: "outline" },
    layout: "default",
    frappeFieldtype: "Select",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.PHONE,
    component: Phone,
    props: { variant: "outline" },
    layout: "default",
    frappeFieldtype: "Phone",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.SWITCH,
    component: Switch,
    props: {},
    layout: "inline",
    frappeFieldtype: "Check",
    isBoolean: true,
    isDate: false,
  },
  {
    name: Fieldtype.TEXTAREA,
    component: Textarea,
    props: { variant: "outline" },
    layout: "default",
    frappeFieldtype: "Text",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.TEXT_EDITOR,
    component: TextEditor,
    props: {
      editorClass:
        "bg-surface-white w-full rounded-b form-description border rounded-b min-h-24",
      fixedMenu: true,
      bubbleMenu: true,
      starterkitOptions: { heading: { levels: [2, 3, 4] } },
    },
    layout: "description-first",
    frappeFieldtype: "Text Editor",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.LINK,
    component: Select,
    props: { variant: "outline" },
    layout: "default",
    frappeFieldtype: "Link",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.CHECKBOX,
    component: Checkbox,
    props: {},
    layout: "inline",
    frappeFieldtype: "Check",
    isBoolean: true,
    isDate: false,
  },
  {
    name: Fieldtype.RATING,
    component: Rating,
    props: {},
    layout: "default",
    frappeFieldtype: "Rating",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.TABLE,
    component: Table,
    props: {
      options: {
        emptyState: {
          title: "This is a table field",
          description: "Use this field to input a list of items.",
        },
      },
    },
    layout: "custom",
    frappeFieldtype: "Table",
    isBoolean: false,
    isDate: false,
  },
  {
    name: Fieldtype.MULTISELECT,
    component: Multiselect,
    props: {},
    layout: "default",
    frappeFieldtype: "JSON",
    isBoolean: false,
    isDate: false,
  },
];

export const FIELD_TYPE_MAP = new Map<Fieldtype, FieldTypeDefinition>(
  FIELD_TYPE_DEFINITIONS.map((d) => [d.name, d])
);

export function getFieldTypeDef(
  name: Fieldtype
): FieldTypeDefinition | undefined {
  return FIELD_TYPE_MAP.get(name);
}
