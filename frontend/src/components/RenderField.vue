<script setup>
import { formFields } from "@/utils/form_fields";
import { computed, ref, watch, onMounted } from "vue";
import { createResource } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { useSubmissionForm } from "@/stores/submissionForm";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
    parentDoctype: {
        type: String,
        default: null,
    },
    themeColor: {
        type: String,
        default: '#3b82f6'
    },
});

const editFormStore = useEditForm();
const submissionFormStore = useSubmissionForm();

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

// Get the parent doctype - from prop or from store (check both edit and submission stores)
const parentDoctype = computed(() => {
    return props.parentDoctype || 
           editFormStore.formData?.linked_doctype || 
           submissionFormStore.formResource?.data?.linked_doctype || 
           null;
});

// Fetch options for Link fields
const fetchLinkOptions = async (searchTerm = null) => {
    if (!doctypeName.value || fetchFailed.value) return;
    
    isLoadingOptions.value = true;
    try {
        const optionsResource = createResource({
            url: "forms_pro.api.form.get_link_field_options",
            makeParams() {
                const params = {
                    doctype: doctypeName.value,
                    search_term: searchTerm,
                    limit: 100,
                };
                
                // Add parent doctype and fieldname if available
                if (parentDoctype.value && props.field.fieldname) {
                    params.parent_doctype = parentDoctype.value;
                    params.fieldname = props.field.fieldname;
                    console.log("RenderField: Sending filter params", {
                        parent_doctype: parentDoctype.value,
                        fieldname: props.field.fieldname,
                        doctype: doctypeName.value
                    });
                } else {
                    console.log("RenderField: Missing filter params", {
                        parentDoctype: parentDoctype.value,
                        fieldname: props.field.fieldname,
                        doctype: doctypeName.value
                    });
                }
                
                return params;
            },
        });
        
        await optionsResource.fetch();
        const options = optionsResource.data?.options || [];
        
        // If we got options, use them
        if (options.length > 0) {
            linkOptions.value = options;
            fetchFailed.value = false; // Reset failed flag if we got results
        } else {
            // No options returned - this could mean:
            // 1. Filters are too restrictive (no matching records)
            // 2. API error
            // 3. Not a valid DocType
            console.warn("RenderField: No options returned for", {
                doctype: doctypeName.value,
                parent_doctype: parentDoctype.value,
                fieldname: props.field.fieldname,
                response: optionsResource.data
            });
            // Don't mark as failed immediately - might be legitimate empty result
            // (e.g., filters are too restrictive and no records match)
            // Keep linkOptions as empty array so we don't fall back to showing DocType name
            linkOptions.value = []; // Set to empty array, not null
        }
    } catch (error) {
        console.error("Error fetching link options:", error, {
            doctype: doctypeName.value,
            parent_doctype: parentDoctype.value,
            fieldname: props.field.fieldname
        });
        // Mark as failed so we don't keep trying
        fetchFailed.value = true;
        linkOptions.value = []; // Set to empty array, not null
    } finally {
        isLoadingOptions.value = false;
    }
};

// Watch for when options are loaded and clear value if it's the DocType name
watch([linkOptions, doctypeName], ([options, doctype]) => {
    if (isLinkField.value && doctype && value.value === doctype) {
        // If the current value is the DocType name, clear it
        // This happens when filters return no results and the field had the DocType name as value
        if (options && options.length === 0) {
            value.value = null;
        } else if (options && options.length > 0) {
            // If we have options but the value is still the DocType name, clear it
            const hasMatchingOption = options.some((opt) => opt.value === doctype);
            if (!hasMatchingOption) {
                value.value = null;
            }
        }
    }
}, { immediate: true });

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
    
    // If it's a Link field but we got empty results, return empty array
    // Don't fall back to showing the DocType name as an option
    if (isLinkField.value && doctypeName.value) {
        // Still loading - return empty for now
        if (isLoadingOptions.value) {
            return [];
        }
        // Fetch completed but got empty results - return empty (don't show DocType name)
        if (linkOptions.value && linkOptions.value.length === 0) {
            return [];
        }
        // Haven't fetched yet - return empty
        if (!linkOptions.value) {
            return [];
        }
    }
    
    // IMPORTANT: For Link fields, never parse the options string as regular options
    // The options string for Link fields is the DocType name, not a list of options
    if (isLinkField.value && doctypeName.value) {
        // This is a Link field - we should only use fetched options
        // If we haven't fetched or got empty results, return empty array
        return [];
    }
    
    // If fetch failed or not a link field, parse the options string (newline-separated values)
    if (props.field.options) {
        const optionsStr = props.field.options.trim();
        
        // Parse newline-separated options (for non-Link Select fields)
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
    <div class="render-field-wrapper" style="position: relative; z-index: 1;">
        <component
            v-model="value"
            :is="getComponent.component"
            :field="props.field"
            v-bind="getBinds"
        />
    </div>
</template>

<style scoped>
.render-field-wrapper {
    position: relative;
}

/* Ensure popups from form fields appear above form container */
:deep(.v-calendar),
:deep(.v-date-picker),
:deep(.v-popover),
:deep(.v-dropdown),
:deep(.v-menu),
:deep([data-popper-placement]),
:deep(.date-picker-popup),
:deep(.calendar-popup),
:deep(.popover-content),
:deep(.dropdown-menu) {
    z-index: 9999 !important;
}
</style>
