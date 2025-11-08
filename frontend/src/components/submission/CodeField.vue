<template>
    <div class="code-field-wrapper">
        <Textarea
            :model-value="codeValue"
            @update:model-value="handleInput"
            variant="outline"
            :placeholder="props.field.placeholder || 'Enter code...'"
            rows="10"
            class="font-mono text-sm"
        />
        <p v-if="props.field.description" class="text-xs text-muted-foreground mt-1">
            {{ props.field.description }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Textarea } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const codeValue = ref(props.modelValue || '');

watch(() => props.modelValue, (value) => {
    codeValue.value = value || '';
}, { immediate: true });

function handleInput(value: string) {
    codeValue.value = value;
    emit('update:modelValue', value || null);
}
</script>

<style scoped>
.code-field-wrapper :deep(textarea) {
    font-family: 'Courier New', Courier, monospace;
    tab-size: 4;
}
</style>

