import {
  Checkbox,
  FormControl,
  DatePicker,
  DateRangePicker,
  DateTimePicker,
  FileUploader,
  Rating,
  Select,
  Switch,
  Textarea,
  TextEditor,
  TimePicker,
  Password,
} from "frappe-ui";
import TableField from "@/components/submission/TableField.vue";
import SignatureField from "@/components/submission/SignatureField.vue";
import PercentField from "@/components/submission/PercentField.vue";
import ReadOnlyField from "@/components/submission/ReadOnlyField.vue";
import ColorField from "@/components/submission/ColorField.vue";
import AutocompleteField from "@/components/submission/AutocompleteField.vue";
import CodeField from "@/components/submission/CodeField.vue";
import DurationField from "@/components/submission/DurationField.vue";
import JSONField from "@/components/submission/JSONField.vue";
import ImageField from "@/components/submission/ImageField.vue";
import GeolocationField from "@/components/submission/GeolocationField.vue";
import DynamicLinkField from "@/components/submission/DynamicLinkField.vue";
import TableMultiSelectField from "@/components/submission/TableMultiSelectField.vue";
import BarcodeField from "@/components/submission/BarcodeField.vue";
import HTMLEditorField from "@/components/submission/HTMLEditorField.vue";
import MarkdownEditorField from "@/components/submission/MarkdownEditorField.vue";

// Individual form field components as dictionaries
export const DataField = {
  component: FormControl,
  props: { type: "text", variant: "outline" },
};

export const NumberField = {
  component: FormControl,
  props: { type: "number", variant: "outline" },
};

export const EmailField = {
  component: FormControl,
  props: { type: "email", variant: "outline" },
};

export const DateField = {
  component: DatePicker,
  props: {
    variant: "outline",
    clearable: true,
    format: "D MMM YYYY",
  },
};

export const DateTimeField = {
  component: DateTimePicker,
  props: {
    format: "DD MMM YYYY, hh:mm A",
    clearable: true,
    variant: "outline",
  },
};

export const DateRangeField = {
  component: DateRangePicker,
  props: {
    clearable: true,
    variant: "outline",
    format: "DD MMM 'YY",
  },
};

export const TimeField = {
  component: TimePicker,
  props: {
    variant: "outline",
    use12Hour: true,
    clearable: true,
  },
};

export const PasswordField = {
  component: Password,
  props: {
    variant: "outline",
  },
};

export const RatingField = {
  component: Rating,
  props: {},
};

export const SelectField = {
  component: Select,
  props: {
    variant: "outline",
  },
};

export const SwitchField = {
  component: Switch,
  props: {},
};

export const TextareaField = {
  component: Textarea,
  props: {
    variant: "outline",
  },
};

export const TextEditorField = {
  component: TextEditor,
  props: {
    editorClass: "bg-surface-white w-full rounded-b form-description border rounded-b min-h-24",
    fixedMenu: true,
    bubbleMenu: true,
    starterkitOptions: {
      heading: {
        levels: [2, 3, 4],
      },
    },
  },
};

export const CheckboxField = {
  component: Checkbox,
  props: {},
};

export const FileUploaderField = {
  component: FileUploader,
  props: {
    variant: "outline",
  },
};

export const CurrencyField = {
  component: FormControl,
  props: { 
    type: "number", 
    variant: "outline",
    step: "0.01",
  },
};

export const IntField = {
  component: FormControl,
  props: { 
    type: "number", 
    variant: "outline",
    step: "1",
  },
};

export const FloatField = {
  component: FormControl,
  props: { 
    type: "number", 
    variant: "outline",
    step: "any",
  },
};

export const PhoneField = {
  component: FormControl,
  props: { 
    type: "tel", 
    variant: "outline",
  },
};

export const TableFieldComponent = {
  component: TableField,
  props: {},
};

export const SignatureFieldComponent = {
  component: SignatureField,
  props: {},
};

export const PercentFieldComponent = {
  component: PercentField,
  props: {},
};

export const ReadOnlyFieldComponent = {
  component: ReadOnlyField,
  props: {},
};

export const ColorFieldComponent = {
  component: ColorField,
  props: {},
};

export const AutocompleteFieldComponent = {
  component: AutocompleteField,
  props: {},
};

export const CodeFieldComponent = {
  component: CodeField,
  props: {},
};

export const DurationFieldComponent = {
  component: DurationField,
  props: {},
};

export const JSONFieldComponent = {
  component: JSONField,
  props: {},
};

export const ImageFieldComponent = {
  component: ImageField,
  props: {},
};

export const GeolocationFieldComponent = {
  component: GeolocationField,
  props: {},
};

export const DynamicLinkFieldComponent = {
  component: DynamicLinkField,
  props: {},
};

export const TableMultiSelectFieldComponent = {
  component: TableMultiSelectField,
  props: {},
};

export const BarcodeFieldComponent = {
  component: BarcodeField,
  props: {},
};

export const HTMLEditorFieldComponent = {
  component: HTMLEditorField,
  props: {},
};

export const MarkdownEditorFieldComponent = {
  component: MarkdownEditorField,
  props: {},
};

export const formFields = [
  { name: "Data", ...DataField },
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
  { name: "File Uploader", ...FileUploaderField },
  { name: "Currency", ...CurrencyField },
  { name: "Int", ...IntField },
  { name: "Float", ...FloatField },
  { name: "Phone", ...PhoneField },
  { name: "Table", ...TableFieldComponent },
  { name: "Signature", ...SignatureFieldComponent },
  { name: "Percent", ...PercentFieldComponent },
  { name: "Read Only", ...ReadOnlyFieldComponent },
  { name: "Color", ...ColorFieldComponent },
  { name: "Autocomplete", ...AutocompleteFieldComponent },
  { name: "Code", ...CodeFieldComponent },
  { name: "Duration", ...DurationFieldComponent },
  { name: "JSON", ...JSONFieldComponent },
  { name: "Image", ...ImageFieldComponent },
  { name: "Geolocation", ...GeolocationFieldComponent },
  { name: "Dynamic Link", ...DynamicLinkFieldComponent },
  { name: "Table MultiSelect", ...TableMultiSelectFieldComponent },
  { name: "Barcode", ...BarcodeFieldComponent },
  { name: "HTML Editor", ...HTMLEditorFieldComponent },
  { name: "Markdown Editor", ...MarkdownEditorFieldComponent },
];

export const mapDoctypeFieldForForm = (fieldtype: string): string => {
  const FIELD_TYPE_MAP: Record<string, string> = {
    // Text fields
    Data: "Data",
    "Small Text": "Textarea",
    Text: "Textarea",
    "Long Text": "Textarea",
    "Text Editor": "Text Editor",
    "HTML Editor": "HTML Editor",
    "Markdown Editor": "Markdown Editor",
    Code: "Code",
    JSON: "JSON",
    
    // Number fields
    Int: "Int",
    Float: "Float",
    Currency: "Currency",
    Percent: "Percent",
    
    // Date/Time fields
    Date: "Date",
    Datetime: "Date Time",
    Time: "Time Picker",
    Duration: "Duration",
    
    // Selection fields
    Select: "Select",
    Autocomplete: "Autocomplete",
    
    // Boolean fields
    Check: "Checkbox",
    
    // Link fields
    Link: "Select", // Link fields become Select dropdowns
    "Dynamic Link": "Dynamic Link",
    
    // File/Attachment fields
    Attach: "File Uploader",
    "Attach Image": "File Uploader",
    Image: "Image",
    Signature: "Signature",
    
    // Special fields
    Password: "Password",
    Rating: "Rating",
    Color: "Color",
    Geolocation: "Geolocation",
    Phone: "Phone", // Phone with validation
    Email: "Email", // Email field type
    
    // Read-only/Display fields
    "Read Only": "Read Only",
    Heading: "Data", // Heading as Data
    HTML: "Textarea", // HTML content as Textarea
    Icon: "Data", // Icon field as Data
    Barcode: "Barcode",
    
    // Layout fields (filtered out but included for completeness)
    "Section Break": "Section Break", // Will be filtered
    "Column Break": "Column Break", // Will be filtered
    "Tab Break": "Tab Break", // Will be filtered
    Fold: "Fold", // Will be filtered
    Button: "Button", // Will be filtered
    
    // Table fields (child tables)
    Table: "Table", // Child tables with full component support
    "Table MultiSelect": "Table MultiSelect",
  };

  // Return mapped type or default to "Data" if not found
  return FIELD_TYPE_MAP[fieldtype] || "Data";
};
