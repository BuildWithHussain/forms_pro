<script setup lang="ts">
import { FormFields, formFields, FormFieldType } from "@/utils/form_fields";
import { computed } from "vue";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
});

const value = defineModel();
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
        v-bind="getComponent.props"
    />
</template>
