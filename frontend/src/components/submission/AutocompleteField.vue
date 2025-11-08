<template>
    <div class="autocomplete-field-wrapper">
        <Combobox
            v-model="selectedValue"
            :options="options"
            :loading="isLoading"
            :placeholder="props.field.placeholder || 'Type to search...'"
            @search="handleSearch"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Combobox } from 'frappe-ui';
import { FormField } from '@/types/formfield';
import { call } from 'frappe-ui';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const selectedValue = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value),
});

const options = ref<Array<{ label: string; value: string }>>([]);
const isLoading = ref(false);

// Parse options from field.options (can be newline-separated or comma-separated)
const staticOptions = computed(() => {
    if (!props.field.options) return [];
    const opts = props.field.options.split(/\n|,/).map(s => s.trim()).filter(s => s);
    return opts.map(opt => ({ label: opt, value: opt }));
});

// Watch for changes in field.options
watch(() => props.field.options, () => {
    if (staticOptions.value.length > 0) {
        options.value = staticOptions.value;
    }
}, { immediate: true });

async function handleSearch(searchTerm: string) {
    if (!searchTerm || searchTerm.length < 2) {
        // Use static options if available
        if (staticOptions.value.length > 0) {
            options.value = staticOptions.value.filter(opt => 
                opt.label.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        return;
    }

    // If field.options is a DocType, fetch options dynamically
    const doctypeName = props.field.options?.trim();
    if (doctypeName && !doctypeName.includes('\n') && !doctypeName.includes(',')) {
        try {
            isLoading.value = true;
            // Use the same API as Link fields for autocomplete
            const response = await call('forms_pro.api.form.get_link_field_options', {
                doctype: doctypeName,
                fieldname: props.field.fieldname,
                search_term: searchTerm,
            });
            
            if (response && response.options) {
                options.value = response.options.map((opt: string) => ({
                    label: opt,
                    value: opt,
                }));
            }
        } catch (error) {
            // Silently handle error - user will see empty options
        } finally {
            isLoading.value = false;
        }
    } else if (staticOptions.value.length > 0) {
        // Filter static options
        options.value = staticOptions.value.filter(opt => 
            opt.label.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
}
</script>

