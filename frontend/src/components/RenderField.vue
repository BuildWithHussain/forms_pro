<script setup>
import { formFields } from "@/utils/form_fields";
import { computed } from "vue";
const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
});

const value = defineModel();
const getComponent = computed(() => {
    return formFields.find((field) => field.name === props.field.fieldtype);
});

const getBinds = computed(() => {
    return {
        ...props.field,
        ...props.field.options,
        ...props.field.default,
    };
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
