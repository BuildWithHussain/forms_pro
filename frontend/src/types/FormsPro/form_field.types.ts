export enum Fieldtype {
  "ATTACH" = "Attach",
  "DATA" = "Data",
  "NUMBER" = "Number",
  "EMAIL" = "Email",
  "DATE" = "Date",
  "DATE_TIME" = "Date Time",
  "DATE_RANGE" = "Date Range",
  "TIME_PICKER" = "Time Picker",
  "PASSWORD" = "Password",
  "SELECT" = "Select",
  "SWITCH" = "Switch",
  "TEXTAREA" = "Textarea",
  "TEXT_EDITOR" = "Text Editor",
  "LINK" = "Link",
  "CHECKBOX" = "Checkbox",
  "RATING" = "Rating",
  "PHONE" = "Phone",
  "TABLE" = "Table",
  "MULTISELECT" = "Multiselect",
  "HEADING_1" = "Heading 1",
  "HEADING_2" = "Heading 2",
  "HEADING_3" = "Heading 3",
  "PAGE_BREAK" = "Page Break",
}

export interface FormField {
  name: string;
  creation: string;
  modified: string;
  owner: string;
  modified_by: string;
  docstatus: 0 | 1 | 2;
  parent?: string;
  parentfield?: string;
  parenttype?: string;
  idx?: number;
  /**	Row Index : Int	*/
  row_index?: number;
  /**	Column Index : Int	*/
  column_index?: number;
  /**	Cell Index : Int	*/
  cell_index?: number;
  /**	Mandatory : Check	*/
  reqd?: 0 | 1;
  /**	Hidden : Check	*/
  hidden?: 0 | 1;
  /**	Label : Data	*/
  label: string;
  /**	Fieldtype : Select	*/
  fieldtype: Fieldtype;
  /**	Fieldname : Data	*/
  fieldname: string;
  /**	Description : Small Text	*/
  description?: string;
  /**	Options : Small Text	*/
  options?: string;
  /**	Default : Small Text	*/
  default?: string;
  /**	Conditional Logic : Code	*/
  conditional_logic?: string;
}
