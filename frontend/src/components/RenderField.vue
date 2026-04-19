<script setup lang="ts">
import type { SelectOption } from "@/utils/selectOptions";
import { useFieldOptions } from "@/utils/selectOptions";
import { FormFields, formFields, FormFieldType } from "@/utils/form_fields";
import type { PropType } from "vue";
import { computed } from "vue";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
    /** Optional pre-loaded options for Select/Link fields. When not provided, options are loaded via useFieldOptions. */
    options: {
        type: Array as PropType<string[] | SelectOption[] | null>,
        required: false,
        default: undefined,
    },
});

const value = defineModel();
const fieldRef = computed(() => props.field);
const { options: loadedOptions } = useFieldOptions(fieldRef);
const resolvedOptions = computed(() => props.options ?? loadedOptions.value);

const getComponent = computed(() => {
    return formFields.find(
        (field: FormFields) => field.name === props.field.fieldtype
    ) as FormFieldType;
});
</script>
<template>
    <component
        v-model="value"
        :is="getComponent.component"
        :field="props.field"
        :options="resolvedOptions"
        v-bind="getComponent.props"
    />
</template>
