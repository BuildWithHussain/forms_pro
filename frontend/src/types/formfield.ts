export enum FormFieldTypes {
  Attach = "Attach",
  Data = "Data",
  Number = "Number",
  Email = "Email",
  Date = "Date",
  DateTime = "Date Time",
  DateRange = "Date Range",
  TimePicker = "Time Picker",
  Password = "Password",
  Select = "Select",
  Phone = "Phone",
  Switch = "Switch",
  Textarea = "Textarea",
  TextEditor = "Text Editor",
  Link = "Link",
  Checkbox = "Checkbox",
  Rating = "Rating",
  Table = "Table",
}

export type FormField = {
  label: string;
  fieldname: string;
  fieldtype: FormFieldTypes;
  description?: string;
  reqd?: boolean;
  hidden?: boolean;
  options?: string;
  default?: string;
  idx?: number;
  conditional_logic?: string;
};
