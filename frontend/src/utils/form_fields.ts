import {
  Checkbox,
  FormControl,
  DatePicker,
  DateRangePicker,
  DateTimePicker,
  Rating,
  Select,
  Switch,
  Textarea,
  TextEditor,
  TimePicker,
  Password,
} from "frappe-ui";
import { Component } from "vue";
import Attachment from "@/components/fields/Attachment.vue";
import Phone from "@/components/fields/Phone.vue";

export type FormFieldType = {
  component: Component;
  props: Record<string, any>;
};

export type FormFields = FormFieldType & {
  name: string;
};

// Individual form field components as dictionaries

export const AttachmentField: FormFieldType = {
  component: Attachment,
  props: {
    variant: "outline",
    filetypes: ["image/*", ".jpg", ".gif", ".pdf"],
  },
};

export const DataField: FormFieldType = {
  component: FormControl,
  props: { type: "text", variant: "outline" },
};

export const NumberField: FormFieldType = {
  component: FormControl,
  props: { type: "number", variant: "outline" },
};

export const EmailField: FormFieldType = {
  component: FormControl,
  props: { type: "email", variant: "outline" },
};

export const DateField: FormFieldType = {
  component: DatePicker,
  props: {
    variant: "outline",
    clearable: true,
    format: "D MMM YYYY",
  },
};

export const DateTimeField: FormFieldType = {
  component: DateTimePicker,
  props: {
    format: "DD MMM YYYY, hh:mm A",
    clearable: true,
    variant: "outline",
  },
};

export const DateRangeField: FormFieldType = {
  component: DateRangePicker,
  props: {
    clearable: true,
    variant: "outline",
    format: "DD MMM 'YY",
  },
};

export const TimeField: FormFieldType = {
  component: TimePicker,
  props: {
    variant: "outline",
    use12Hour: true,
    clearable: true,
  },
};

export const PasswordField: FormFieldType = {
  component: Password,
  props: {
    variant: "outline",
  },
};

export const RatingField: FormFieldType = {
  component: Rating,
  props: {},
};

export const SelectField: FormFieldType = {
  component: Select,
  props: {
    variant: "outline",
  },
};

export const SwitchField: FormFieldType = {
  component: Switch,
  props: {},
};

export const TextareaField: FormFieldType = {
  component: Textarea,
  props: {
    variant: "outline",
  },
};

export const TextEditorField: FormFieldType = {
  component: TextEditor,
  props: {
    editorClass:
      "bg-surface-white w-full rounded-b form-description border rounded-b min-h-24",
    fixedMenu: true,
    bubbleMenu: true,
    starterkitOptions: {
      heading: {
        levels: [2, 3, 4],
      },
    },
  },
};

export const CheckboxField: FormFieldType = {
  component: Checkbox,
  props: {},
};

export const PhoneField: FormFieldType = {
  component: Phone,
  props: {
    variant: "outline",
  },
};

export const formFields: FormFields[] = [
  { name: "Attach", ...AttachmentField },
  { name: "Data", ...DataField },
  { name: "Link", ...SelectField },
  { name: "Number", ...NumberField },
  { name: "Email", ...EmailField },
  { name: "Date", ...DateField },
  { name: "Date Time", ...DateTimeField },
  { name: "Date Range", ...DateRangeField },
  { name: "Time Picker", ...TimeField },
  { name: "Password", ...PasswordField },
  { name: "Rating", ...RatingField },
  { name: "Select", ...SelectField },
  { name: "Switch", ...SwitchField },
  { name: "Textarea", ...TextareaField },
  { name: "Text Editor", ...TextEditorField },
  { name: "Checkbox", ...CheckboxField },
  { name: "Phone", ...PhoneField },
];

export const mapDoctypeFieldForForm = (fieldtype: string): string => {
  const FIELD_TYPE_MAP = {
    Autocomplete: "Data",
    Attach: "Attach",
    "Attach Image": "Attach",
    Barcode: "Barcode",
    Button: "Button",
    Check: "Checkbox",
    Code: "Code",
    Color: "Color",
    "Column Break": "Column Break",
    Currency: "Number",
    Data: "Data",
    Date: "Date",
    Datetime: "Date Time",
    Duration: "Duration",
    "Dynamic Link": "Dynamic Link",
    Float: "Number",
    Fold: "Fold",
    Geolocation: "Geolocation",
    Heading: "Heading",
    HTML: "HTML",
    "HTML Editor": "Text Editor",
    Icon: "Icon",
    Image: "Image",
    Int: "Number",
    JSON: "JSON",
    Link: "Link",
    "Long Text": "Textarea",
    "Markdown Editor": "Text Editor",
    Password: "Password",
    Percent: "Number",
    Phone: "Phone",
    "Read Only": "Read Only",
    Rating: "Rating",
    "Section Break": "Section Break",
    Select: "Select",
    Signature: "Signature",
    "Small Text": "Textarea",
    "Tab Break": "Tab Break",
    Table: "Table",
    "Table MultiSelect": "Table MultiSelect",
    Text: "Textarea",
    "Text Editor": "Text Editor",
    Time: "Time",
  };

  return FIELD_TYPE_MAP[fieldtype as keyof typeof FIELD_TYPE_MAP];
};
