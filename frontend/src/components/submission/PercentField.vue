<template>
    <div class="percent-field-wrapper">
        <FormControl
            :model-value="displayValue"
            @update:model-value="handleInput"
            type="number"
            variant="outline"
            :placeholder="props.field.placeholder || 'Enter percentage'"
            :min="0"
            :max="100"
            step="0.01"
        />
        <span class="ml-2 text-sm text-muted-foreground">%</span>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FormControl } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: number | string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: number | null];
}>();

const displayValue = computed(() => {
    if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
        return null;
    }
    // Convert to number if string
    const numValue = typeof props.modelValue === 'string' ? parseFloat(props.modelValue) : props.modelValue;
    return isNaN(numValue) ? null : numValue;
});

function handleInput(value: string | number | null) {
    if (value === null || value === '' || value === undefined) {
        emit('update:modelValue', null);
        return;
    }
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    emit('update:modelValue', isNaN(numValue) ? null : numValue);
}
</script>

<style scoped>
.percent-field-wrapper {
    display: flex;
    align-items: center;
}
</style>

