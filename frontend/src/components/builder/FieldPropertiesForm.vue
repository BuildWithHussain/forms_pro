<script setup lang="ts">
import { useEditForm } from "@/stores/editForm";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";

const editFormStore = useEditForm();

// Helper function to mark form as dirty when field properties change
function markFormDirty() {
    if (editFormStore.formResource?.doc && editFormStore.selectedField) {
        // Find the field in the fields array and update it to trigger reactivity
        const fieldIndex = editFormStore.formResource.doc.fields.findIndex(
            (f: any) => f === editFormStore.selectedField
        );
        if (fieldIndex !== -1) {
            // Create a new object reference to trigger reactivity and mark as dirty
            // This ensures the formResource detects the change
            const updatedField = {
                ...editFormStore.selectedField
            };
            editFormStore.formResource.doc.fields[fieldIndex] = updatedField;
            // Restore the reference to maintain the connection
            editFormStore.selectedField = updatedField;
            
            // Force the formResource to recognize the change
            // The createDocumentResource should automatically detect this, but we ensure it does
            if (editFormStore.formResource.setValue) {
                // Touch the setValue to ensure dirty state is tracked
                editFormStore.formResource.doc = {
                    ...editFormStore.formResource.doc,
                    fields: [...editFormStore.formResource.doc.fields]
                };
            }
        }
    }
}

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
        "Signature",
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
        <h3 class="text-lg font-semibold">Edit Properties</h3>
        <Separator />
        <div class="flex flex-col gap-6 w-full">
            <template v-for="property in getFieldProperties()" :key="property.label">
                <div v-if="property.type === 'text'" class="flex flex-col gap-2">
                    <Label :for="property.field">
                        {{ property.label }}
                        <span v-if="property.required" class="text-destructive">*</span>
                    </Label>
                    <Input
                        :id="property.field"
                        :model-value="editFormStore.selectedField[property.field]"
                        @update:model-value="(value) => {
                            if (editFormStore.selectedField) {
                                editFormStore.selectedField[property.field] = value;
                                markFormDirty();
                            }
                        }"
                        :required="property.required"
                    />
                </div>
                <div v-else-if="property.type === 'select'" class="flex flex-col gap-2">
                    <Label :for="property.field">
                        {{ property.label }}
                        <span v-if="property.required" class="text-destructive">*</span>
                    </Label>
                    <Select
                        :model-value="editFormStore.selectedField[property.field]"
                        @update:model-value="(value) => {
                            if (editFormStore.selectedField && value) {
                                editFormStore.selectedField[property.field] = value;
                                markFormDirty();
                            }
                        }"
                    >
                        <SelectTrigger :id="property.field">
                            <SelectValue :placeholder="`Select ${property.label}`" />
                        </SelectTrigger>
                        <SelectContent class="z-[100]">
                            <SelectItem
                                v-for="option in property.options"
                                :key="option"
                                :value="option"
                            >
                                {{ option }}
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div v-else-if="property.type === 'textarea'" class="flex flex-col gap-2">
                    <Label :for="property.field">
                        {{ property.label }}
                        <span v-if="property.required" class="text-destructive">*</span>
                    </Label>
                    <Textarea
                        :id="property.field"
                        :model-value="editFormStore.selectedField[property.field]"
                        @update:model-value="(value) => {
                            if (editFormStore.selectedField) {
                                editFormStore.selectedField[property.field] = value;
                                markFormDirty();
                            }
                        }"
                        :required="property.required"
                    />
                </div>
                <div v-else-if="property.type === 'checkbox'" class="flex items-center gap-2">
                    <Checkbox
                        :id="property.field"
                        :checked="editFormStore.selectedField[property.field]"
                        @update:checked="(checked) => {
                            if (editFormStore.selectedField) {
                                editFormStore.selectedField[property.field] = checked;
                                markFormDirty();
                            }
                        }"
                    />
                    <Label :for="property.field" class="cursor-pointer">
                        {{ property.label }}
                        <span v-if="property.required" class="text-destructive">*</span>
                    </Label>
                </div>
            </template>
        </div>
    </div>
</template>
