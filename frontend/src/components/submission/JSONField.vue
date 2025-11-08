<template>
    <div class="json-field-wrapper">
        <Textarea
            :model-value="jsonString"
            @update:model-value="handleInput"
            variant="outline"
            :placeholder="props.field.placeholder || 'Enter JSON...'"
            rows="6"
            class="font-mono text-sm"
            :class="{ 'border-destructive': hasError }"
        />
        <p v-if="hasError" class="text-xs text-destructive mt-1">
            Invalid JSON: {{ errorMessage }}
        </p>
        <p v-else-if="jsonString && isValid" class="text-xs text-muted-foreground mt-1">
            Valid JSON
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Textarea } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: string | object | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const jsonString = ref('');
const hasError = ref(false);
const errorMessage = ref('');
const isValid = ref(false);

// Parse modelValue to JSON string
watch(() => props.modelValue, (value) => {
    if (value === null || value === undefined || value === '') {
        jsonString.value = '';
        hasError.value = false;
        isValid.value = false;
        return;
    }
    
    if (typeof value === 'string') {
        jsonString.value = value;
        validateJSON(value);
    } else {
        try {
            jsonString.value = JSON.stringify(value, null, 2);
            isValid.value = true;
            hasError.value = false;
        } catch (e) {
            jsonString.value = String(value);
            hasError.value = true;
            errorMessage.value = String(e);
        }
    }
}, { immediate: true });

function validateJSON(str: string) {
    if (!str.trim()) {
        isValid.value = false;
        hasError.value = false;
        return;
    }
    
    try {
        JSON.parse(str);
        isValid.value = true;
        hasError.value = false;
        errorMessage.value = '';
    } catch (e: any) {
        isValid.value = false;
        hasError.value = true;
        errorMessage.value = e.message || 'Invalid JSON format';
    }
}

function handleInput(value: string) {
    jsonString.value = value;
    validateJSON(value);
    
    if (isValid.value && value.trim()) {
        emit('update:modelValue', value);
    } else if (!value.trim()) {
        emit('update:modelValue', null);
    } else {
        // Still emit the value even if invalid, so user can continue editing
        emit('update:modelValue', value);
    }
}
</script>

