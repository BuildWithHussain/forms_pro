<script setup lang="ts">
import { useEditForm } from "@/stores/editForm";
import { FormControl } from "frappe-ui";
import { FormField, FormFieldTypes } from "@/types/formfield";
import { computed } from "vue";
import type { Component } from "vue";
import ConditionalLogicSection from "./ConditionalLogicSection.vue";

const editFormStore = useEditForm();

type FieldProperty = {
    fieldname: keyof FormField;
    component: Component;
    props: Record<string, any>;
};

const fieldProperties = computed(() => {
    return [
        {
            fieldname: "label",
            component: FormControl,
            props: {
                type: "text",
                label: "Label",
                required: true,
                variant: "outline",
            },
        },
        {
            fieldname: "fieldname",
            component: FormControl,
            props: {
                type: "text",
                label: "Fieldname",
                required: true,
                variant: "outline",
            },
        },
        {
            fieldname: "fieldtype",
            component: FormControl,
            props: {
                type: "select",
                label: "Fieldtype",
                required: true,
                variant: "outline",
                options: Object.values(FormFieldTypes),
            },
        },
        {
            fieldname: "reqd",
            component: FormControl,
            props: {
                type: "checkbox",
                label: "Mandatory",
                description: "If enabled, the field becomes required and cannot be left blank.",
            },
        },
        {
            fieldname: "hidden",
            component: FormControl,
            props: {
                type: "checkbox",
                label: "Hidden",
                description: "If enabled, the field is hidden from the form.",
            },
        },
        {
            fieldname: "description",
            component: FormControl,
            props: {
                type: "textarea",
                label: "Description",
                required: false,
                variant: "outline",
                rows: 5,
            },
        },
        {
            fieldname: "options",
            component: FormControl,
            props: {
                type: "textarea",
                label: "Options",
                description: "Enter the options for the field, one per line.",
                variant: "outline",
                rows: 5,
            },
        },
        {
            fieldname: "default",
            component: FormControl,
            props: {
                type: "text",
                label: "Default Value",
                description: "The default value for the field.",
                variant: "outline",
            },
        },
        {
            fieldname: "conditional_logic",
            component: ConditionalLogicSection,
            props: {},
        },
    ] as FieldProperty[];
});
</script>
<template>
    <div
        class="flex flex-col gap-6 p-4 w-full"
        data-form-builder-component="field-properties-form"
    >
        <h3 class="text-lg font-medium">Edit Properties</h3>
        <hr />
        <template v-if="editFormStore.selectedField">
            <template v-for="property in fieldProperties" :key="property.fieldname">
                <component
                    :is="property.component"
                    v-model="editFormStore.selectedField[property.fieldname]"
                    v-bind="property.props"
                />
            </template>
        </template>
    </div>
</template>
