<script setup>
import { formFields } from "@/utils/form_fields";
import { computed, ref, watch, onMounted } from "vue";
import { createResource } from "frappe-ui";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
});

const value = defineModel();
const linkOptions = ref(null);
const isLoadingOptions = ref(false);

const getComponent = computed(() => {
    return formFields.find((field) => field.name === props.field.fieldtype);
});

// Check if this is a Select field with a DocType name as options
const isLinkField = computed(() => {
    return (
        props.field.fieldtype === "Select" &&
        props.field.options &&
        !props.field.options.includes("\n") && // Not a multi-line options list
        props.field.options.trim().length > 0
    );
});

// Check if options is a valid DocType name
// We'll try to fetch and if it fails, fall back to regular options
const doctypeName = computed(() => {
    if (!isLinkField.value) return null;
    const optionsStr = props.field.options.trim();
    
    // Skip if it looks like a regular options list (has newlines or multiple values)
    if (optionsStr.includes("\n") || optionsStr.split(",").length > 1) {
        return null;
    }
    
    // Try to detect if it's a DocType name
    // DocType names are typically:
    // - Single word or words with spaces
    // - Title Case (first letter uppercase)
    // - No special characters except spaces and underscores
    const isLikelyDocType = /^[A-Z][a-zA-Z0-9_\s]*$/.test(optionsStr);
    
    if (isLikelyDocType && optionsStr.length > 0) {
        return optionsStr;
    }
    
    return null;
});

// Track if we've tried to fetch and failed (so we don't keep trying)
const fetchFailed = ref(false);

// Fetch options for Link fields
const fetchLinkOptions = async (searchTerm = null) => {
    if (!doctypeName.value || fetchFailed.value) return;
    
    isLoadingOptions.value = true;
    try {
        const optionsResource = createResource({
            url: "forms_pro.api.form.get_link_field_options",
            makeParams() {
                return {
                    doctype: doctypeName.value,
                    search_term: searchTerm,
                    limit: 100,
                };
            },
        });
        
        await optionsResource.fetch();
        const options = optionsResource.data?.options || [];
        
        // If we got options, use them; otherwise mark as failed
        if (options.length > 0) {
            linkOptions.value = options;
        } else {
            // No options returned - might not be a valid DocType
            fetchFailed.value = true;
            linkOptions.value = null;
        }
    } catch (error) {
        console.error("Error fetching link options:", error);
        // Mark as failed so we don't keep trying
        fetchFailed.value = true;
        linkOptions.value = null;
    } finally {
        isLoadingOptions.value = false;
    }
};

// Fetch options on mount if it's a link field
onMounted(() => {
    if (isLinkField.value && doctypeName.value) {
        fetchLinkOptions();
    }
});

// Get the options to pass to the Select component
const selectOptions = computed(() => {
    // If it's a Link field with fetched options, use those
    if (isLinkField.value && linkOptions.value && linkOptions.value.length > 0) {
        return linkOptions.value;
    }
    
    // If fetch failed or not a link field, parse the options string (newline-separated values)
    if (props.field.options) {
        const optionsStr = props.field.options.trim();
        
        // If it's a single value and we haven't fetched yet, it might be a DocType
        // But if fetch failed, treat it as a regular option
        if (isLinkField.value && doctypeName.value && !fetchFailed.value && !linkOptions.value) {
            // Still loading or haven't fetched yet - return empty for now
            return [];
        }
        
        // Parse newline-separated options
        const optionsList = optionsStr
            .split("\n")
            .map((opt) => opt.trim())
            .filter((opt) => opt.length > 0);
        
        return optionsList.map((opt) => ({
            label: opt,
            value: opt,
        }));
    }
    
    return [];
});

const getBinds = computed(() => {
    const baseBinds = {
        ...props.field,
        ...getComponent.value?.props,
    };
    
    // For Select fields, override options
    if (props.field.fieldtype === "Select") {
        baseBinds.options = selectOptions.value;
        baseBinds.loading = isLoadingOptions.value;
    }
    
    return baseBinds;
});
</script>
<template>
    <component
        v-model="value"
        :is="getComponent.component"
        :field="props.field"
        v-bind="getBinds"
    />
</template>
