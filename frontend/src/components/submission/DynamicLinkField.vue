<template>
    <div class="dynamic-link-field-wrapper">
        <div class="flex flex-col gap-2">
            <div class="flex items-center gap-2">
                <Combobox
                    v-model="selectedDoctype"
                    :options="doctypeOptions"
                    label="DocType"
                    :loading="doctypesLoading"
                    placeholder="Select DocType"
                    class="flex-1"
                />
            </div>
            <div v-if="selectedDoctype" class="flex items-center gap-2">
                <Combobox
                    v-model="selectedLink"
                    :options="linkOptions"
                    label="Link"
                    :loading="linksLoading"
                    placeholder="Select link"
                    class="flex-1"
                />
            </div>
        </div>
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

const selectedDoctype = ref<string | null>(null);
const selectedLink = ref<string | null>(null);
const doctypeOptions = ref<Array<{ label: string; value: string }>>([]);
const linkOptions = ref<Array<{ label: string; value: string }>>([]);
const doctypesLoading = ref(false);
const linksLoading = ref(false);

// Parse options to get available doctypes (format: "DocType1\nDocType2" or JSON)
const availableDoctypes = computed(() => {
    if (!props.field.options) return [];
    try {
        // Try parsing as JSON first
        const parsed = JSON.parse(props.field.options);
        if (Array.isArray(parsed)) {
            return parsed;
        }
    } catch {
        // Not JSON, treat as newline-separated
        return props.field.options.split('\n').map(s => s.trim()).filter(s => s);
    }
    return [];
});

// Load doctypes on mount
watch(() => props.field.options, async () => {
    if (availableDoctypes.value.length > 0) {
        doctypeOptions.value = availableDoctypes.value.map(dt => ({
            label: dt,
            value: dt,
        }));
    } else {
        // Fetch all doctypes if options not specified
        try {
            doctypesLoading.value = true;
            const response = await call('frappe.client.get_list', {
                doctype: 'DocType',
                fields: ['name'],
                limit_page_length: 1000,
            });
            if (response) {
                doctypeOptions.value = response.map((dt: any) => ({
                    label: dt.name,
                    value: dt.name,
                }));
            }
        } catch (error) {
            console.error('Error fetching doctypes:', error);
        } finally {
            doctypesLoading.value = false;
        }
    }
}, { immediate: true });

// Parse modelValue (format: "DocType|LinkName")
watch(() => props.modelValue, (value) => {
    if (value && value.includes('|')) {
        const [doctype, link] = value.split('|');
        selectedDoctype.value = doctype;
        selectedLink.value = link;
    } else {
        selectedDoctype.value = null;
        selectedLink.value = null;
    }
}, { immediate: true });

// Watch for doctype changes and fetch links
watch(selectedDoctype, async (doctype) => {
    if (!doctype) {
        selectedLink.value = null;
        linkOptions.value = [];
        emit('update:modelValue', null);
        return;
    }
    
    try {
        linksLoading.value = true;
        const response = await call('forms_pro.api.form.get_link_field_options', {
            doctype: doctype,
            fieldname: props.field.fieldname,
        });
        
        if (response && response.options) {
            linkOptions.value = response.options.map((opt: string) => ({
                label: opt,
                value: opt,
            }));
        }
    } catch (error) {
        console.error('Error fetching link options:', error);
        linkOptions.value = [];
    } finally {
        linksLoading.value = false;
    }
});

// Watch for link changes and update modelValue
watch([selectedDoctype, selectedLink], ([doctype, link]) => {
    if (doctype && link) {
        emit('update:modelValue', `${doctype}|${link}`);
    } else {
        emit('update:modelValue', null);
    }
});
</script>

