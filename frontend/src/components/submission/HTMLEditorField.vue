<template>
    <div class="html-editor-field-wrapper">
        <TextEditor
            :model-value="htmlValue"
            @update:model-value="handleInput"
            :editor-class="'bg-surface-white w-full rounded-b form-description border rounded-b min-h-32'"
            :fixed-menu="true"
            :bubble-menu="true"
            :starterkit-options="{
                heading: {
                    levels: [1, 2, 3, 4, 5, 6],
                },
            }"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { TextEditor } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const htmlValue = ref(props.modelValue || '');

watch(() => props.modelValue, (value) => {
    htmlValue.value = value || '';
}, { immediate: true });

function handleInput(value: string) {
    htmlValue.value = value;
    emit('update:modelValue', value || null);
}
</script>

