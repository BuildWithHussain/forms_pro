<script setup>
import { useEditForm } from "@/stores/editForm";
import { FormControl } from "frappe-ui";

const editFormStore = useEditForm();

const getFieldTypeOptions = () => {
    // Must match the options in Form Field DocType (form_field.json)
    return [
        "Data",
        "Number",
        "Email",
        "Date",
        "Date Time",
        "Date Range",
        "Time Picker",
        "Password",
        "Select",
        "Switch",
        "Textarea",
        "Text Editor",
        "Checkbox",
        "File Uploader",
        "Currency",
        "Int",
        "Float",
        "Phone",
        "Table",
        "Rating",
    ];
};

const getFieldProperties = () => {
    return [
        { label: "Label", type: "text", field: "label", required: true },
        {
            label: "Fieldname",
            type: "text",
            field: "fieldname",
            required: true,
        },
        {
            label: "Fieldtype",
            type: "select",
            field: "fieldtype",
            required: true,
            options: getFieldTypeOptions(),
        },
        { label: "Description", type: "textarea", field: "description" },
        { label: "Mandatory", type: "checkbox", field: "reqd" },
        { label: "Options", type: "textarea", field: "options" },
        { label: "Default", type: "textarea", field: "default" },
    ];
};
</script>
<template>
    <div class="flex flex-col gap-6 p-4 w-full">
        <h3 class="text-lg font-medium">Edit Properties</h3>
        <hr />
        <div class="flex flex-col gap-6 w-full">
            <template v-for="property in getFieldProperties()" :key="property.label">
                <FormControl
                    v-model="editFormStore.selectedField[property.field]"
                    :label="property.label"
                    :type="property.type"
                    :required="property.required"
                    :options="property.options"
                />
            </template>
        </div>
    </div>
</template>
