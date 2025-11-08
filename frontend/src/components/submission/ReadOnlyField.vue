<template>
    <div class="readonly-field-wrapper">
        <div class="readonly-display border rounded-md px-3 py-2 bg-muted/50 text-sm">
            {{ displayValue }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: any;
}>();

const displayValue = computed(() => {
    if (props.modelValue === null || props.modelValue === undefined || props.modelValue === '') {
        return props.field.placeholder || '—';
    }
    return String(props.modelValue);
});
</script>

<style scoped>
.readonly-display {
    min-height: 2.5rem;
    display: flex;
    align-items: center;
}
</style>

