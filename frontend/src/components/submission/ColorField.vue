<template>
    <div class="color-field-wrapper">
        <div class="flex items-center gap-2">
            <input
                type="color"
                :value="colorValue"
                @input="handleColorChange"
                class="h-10 w-20 rounded border cursor-pointer"
            />
            <FormControl
                :model-value="colorValue"
                @update:model-value="handleInput"
                type="text"
                variant="outline"
                :placeholder="props.field.placeholder || '#000000'"
                pattern="^#[0-9A-Fa-f]{6}$"
                maxlength="7"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FormControl } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const colorValue = computed(() => {
    if (props.modelValue && /^#[0-9A-Fa-f]{6}$/.test(props.modelValue)) {
        return props.modelValue;
    }
    return props.field.default || '#000000';
});

function handleColorChange(event: Event) {
    const target = event.target as HTMLInputElement;
    emit('update:modelValue', target.value);
}

function handleInput(value: string | null) {
    if (!value) {
        emit('update:modelValue', null);
        return;
    }
    // Validate hex color format
    if (/^#[0-9A-Fa-f]{6}$/.test(value)) {
        emit('update:modelValue', value);
    } else if (/^[0-9A-Fa-f]{6}$/.test(value)) {
        // Add # if missing
        emit('update:modelValue', '#' + value);
    }
}
</script>

