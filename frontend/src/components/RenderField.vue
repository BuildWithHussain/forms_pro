<script setup lang="ts">
import { formFields } from "@/utils/form_fields";
import { computed, ref, watch, onMounted, onUnmounted } from "vue";
import { createResource } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { useSubmissionForm } from "@/stores/submissionForm";
import TableField from "@/components/submission/TableField.vue";

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

// Check if this is a Link field or Select field with a DocType name as options
const isLinkField = computed(() => {
    // If fieldtype is Link, it's definitely a link field
    if (props.field.fieldtype === "Link") {
        return true;
    }
    
    // If fieldtype is Select, check if options looks like a DocType name
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
    
    // For Link fieldtype, options is the DocType name
    if (props.field.fieldtype === "Link" && props.field.options) {
        return props.field.options.trim();
    }
    
    // For Select fields, check if options looks like a DocType name
    const optionsStr = props.field.options?.trim() || '';
    
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

// Get form ID from either edit or submission store
const formId = computed(() => {
    // Try multiple sources for form ID
    return editFormStore.formData?.name || 
           submissionFormStore.formResource?.data?.name ||
           (submissionFormStore.formResource?.data && submissionFormStore.formResource.data.name) ||
           null;
});

// Fetch options for Link fields
const fetchLinkOptions = async (searchTerm = null) => {
    if (!doctypeName.value || fetchFailed.value) return;
    
    // Wait for form to load if in submission mode
    if (submissionFormStore.formResource?.loading) {
        await new Promise((resolve) => {
            const unwatch = watch(() => submissionFormStore.formResource?.loading, (loading) => {
                if (!loading) {
                    unwatch();
                    resolve(null);
                }
            });
        });
    }
    
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
                }
                
                // Add form_id for guest permission checks - always pass if available
                // Try multiple sources to ensure we have the form ID
                const formIdToUse = formId.value || 
                                   submissionFormStore.formResource?.data?.name ||
                                   null;
                
                if (formIdToUse) {
                    params.form_id = formIdToUse;
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
            // Don't mark as failed immediately - might be legitimate empty result
            // (e.g., filters are too restrictive and no records match)
            // Keep linkOptions as empty array so we don't fall back to showing DocType name
            linkOptions.value = []; // Set to empty array, not null
        }
    } catch (error) {
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

// Fetch options immediately on mount if it's a link field
onMounted(() => {
    if (isLinkField.value && doctypeName.value && !linkOptions.value) {
        fetchLinkOptions();
    }
});

// Watch for when isLinkField or doctypeName becomes available and fetch options
watch([isLinkField, doctypeName], ([isLink, doctype]) => {
    if (isLink && doctype && !linkOptions.value && !isLoadingOptions.value) {
        fetchLinkOptions();
    }
}, { immediate: true });

// Handle field click (options are pre-fetched, but keep as fallback)
const handleFieldClick = (event) => {
    // Only handle if it's a Link field and we haven't fetched yet (fallback)
    if (isLinkField.value && doctypeName.value) {
        // Check if click is on the field itself or its children (but not on a popup)
        const target = event.target;
        if (!target.closest('[role="dialog"]') && !target.closest('.popover') && !target.closest('.dropdown-menu')) {
            // Only fetch if we don't have options and aren't already loading
            if ((!linkOptions.value || linkOptions.value.length === 0) && !isLoadingOptions.value && !fetchFailed.value) {
                fetchLinkOptions();
            }
        }
    }
};

// Handle field focus (options are pre-fetched, but keep as fallback)
const handleFieldFocus = (event) => {
    // Only handle if it's a Link field and we haven't fetched yet (fallback)
    if (isLinkField.value && doctypeName.value) {
        // Only fetch if we don't have options and aren't already loading
        if ((!linkOptions.value || linkOptions.value.length === 0) && !isLoadingOptions.value && !fetchFailed.value) {
            fetchLinkOptions();
        }
    }
};

// Fix z-index for date picker popups using MutationObserver
let observer: MutationObserver | null = null;
let interval: number | null = null;

onMounted(() => {
    const fixDatePickerZIndex = () => {
        // Find all potential date picker popups - be very aggressive
        const selectors = [
            '[role="dialog"]',
            '[data-popper-placement]',
            '.v-calendar',
            '.v-date-picker',
            '.calendar',
            '[class*="calendar"]',
            '[class*="date-picker"]',
            '[class*="datepicker"]',
            '[data-calendar]',
            '[data-date-picker]',
            // Frappe UI specific
            '[class*="date"]',
            '[class*="Date"]',
        ];
        
        selectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach((el) => {
                    const htmlEl = el as HTMLElement;
                    // Check if it's a popup (fixed or absolute positioned)
                    const computedStyle = window.getComputedStyle(htmlEl);
                    const position = computedStyle.position;
                    
                    if (position === 'fixed' || position === 'absolute') {
                        // Force maximum z-index and fixed position
                        htmlEl.style.setProperty('z-index', '2147483647', 'important');
                        htmlEl.style.setProperty('position', 'fixed', 'important');
                        
                        // Also check parent elements that might be creating stacking context
                        let parent = htmlEl.parentElement;
                        while (parent && parent !== document.body) {
                            const parentStyle = window.getComputedStyle(parent);
                            // If parent has a stacking context, ensure it doesn't trap the popup
                            if (parentStyle.zIndex && parseInt(parentStyle.zIndex) > 0) {
                                // Don't modify parent, but ensure popup breaks out
                                break;
                            }
                            parent = parent.parentElement;
                        }
                    }
                });
            } catch (e) {
                // Ignore errors for invalid selectors
            }
        });
        
        // Also target any element that looks like a calendar by checking content/structure
        document.querySelectorAll('div').forEach((el) => {
            const htmlEl = el as HTMLElement;
            const computedStyle = window.getComputedStyle(htmlEl);
            const position = computedStyle.position;
            
            // Check if it has calendar-like classes or attributes
            const hasCalendarClass = Array.from(htmlEl.classList).some(cls => 
                cls.toLowerCase().includes('calendar') || 
                cls.toLowerCase().includes('date') ||
                cls.toLowerCase().includes('picker')
            );
            
            const hasCalendarAttr = htmlEl.hasAttribute('data-calendar') || 
                                   htmlEl.hasAttribute('data-date-picker') ||
                                   htmlEl.getAttribute('role') === 'dialog';
            
            if ((hasCalendarClass || hasCalendarAttr) && (position === 'fixed' || position === 'absolute')) {
                htmlEl.style.setProperty('z-index', '2147483647', 'important');
                htmlEl.style.setProperty('position', 'fixed', 'important');
            }
        });
    };
    
    // Run immediately
    fixDatePickerZIndex();
    
    // Watch for new popups being added - more aggressive watching
    observer = new MutationObserver(() => {
        fixDatePickerZIndex();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class', 'role', 'data-popper-placement'],
    });
    
    // Also run on interval as backup - more frequent
    interval = setInterval(fixDatePickerZIndex, 50);
    
    // Also listen for click events on date fields to fix immediately
    document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        // Check if clicked element is a date input or related
        if (target.tagName === 'INPUT' && (target.type === 'date' || target.type === 'text')) {
            const field = target.closest('.render-field-wrapper');
            if (field) {
                // Small delay to let popup render
                setTimeout(fixDatePickerZIndex, 10);
                setTimeout(fixDatePickerZIndex, 50);
                setTimeout(fixDatePickerZIndex, 100);
            }
        }
    }, true);
});

onUnmounted(() => {
    if (observer) {
        observer.disconnect();
    }
    if (interval) {
        clearInterval(interval);
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
    
    // Remove label from binds - FieldRenderer handles labels to avoid duplication
    // FormControl and other components should not render labels automatically
    delete baseBinds.label;
    
    // Remove description from binds - FieldRenderer handles descriptions to avoid duplication
    // FormControl and other components should not render descriptions automatically
    delete baseBinds.description;
    
    // Clear placeholder to prevent label duplication
    // FieldRenderer shows the label separately, so placeholder should be empty or generic
    // Don't use label or fieldname as placeholder
    if (baseBinds.placeholder) {
        const placeholder = String(baseBinds.placeholder).toLowerCase();
        const label = String(props.field.label || "").toLowerCase();
        const fieldname = String(props.field.fieldname || "").toLowerCase();
        
        // If placeholder matches label or fieldname, clear it
        if (placeholder === label || placeholder === fieldname) {
            baseBinds.placeholder = "";
        }
    }
    
    // For Select and Link fields, override options
    if (props.field.fieldtype === "Select" || props.field.fieldtype === "Link") {
        baseBinds.options = selectOptions.value;
        baseBinds.loading = isLoadingOptions.value;
        
        // Options are pre-fetched on mount, so we don't need click/focus handlers
        // But keep them as fallback in case options failed to load initially
        if (isLinkField.value && doctypeName.value) {
            baseBinds.onClick = () => {
                // Only fetch if we don't have options yet (fallback)
                if (!linkOptions.value || linkOptions.value.length === 0) {
                    if (!isLoadingOptions.value && !fetchFailed.value) {
                        fetchLinkOptions();
                    }
                }
            };
        }
    }
    
    return baseBinds;
});
</script>
<template>
    <div 
        class="render-field-wrapper" 
        style="position: relative; z-index: 1;"
        @click="handleFieldClick"
        @focusin="handleFieldFocus"
    >
        <!-- Table Field (Child Tables) -->
        <TableField
            v-if="props.field.fieldtype === 'Table'"
            :field="props.field"
            :model-value="value || []"
            @update:model-value="(val) => value = val"
            :parent-doctype="parentDoctype"
            :theme-color="props.themeColor"
        />
        
        <!-- All other field types -->
        <component
            v-else
            v-model="value"
            :is="getComponent.component"
            :field="props.field"
            v-bind="getBinds"
            :class="{ 'has-dropdown-indicator': (props.field.fieldtype === 'Select' || props.field.fieldtype === 'Link') }"
        />
    </div>
</template>

<style scoped>
.render-field-wrapper {
    position: relative;
}

/* Add dropdown indicator to Select fields */
.render-field-wrapper:has(.has-dropdown-indicator) {
    position: relative;
}

:deep(.has-dropdown-indicator) {
    position: relative;
}

:deep(.has-dropdown-indicator input),
:deep(.has-dropdown-indicator .form-control),
:deep(.has-dropdown-indicator button) {
    padding-right: 2.5rem !important;
}

.render-field-wrapper:has(.has-dropdown-indicator)::after {
    content: '';
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #6b7280;
    pointer-events: none;
    z-index: 10;
}

/* Ensure popups from form fields appear above form container - use maximum z-index */
:deep(.v-calendar),
:deep(.v-date-picker),
:deep(.v-popover),
:deep(.v-dropdown),
:deep(.v-menu),
:deep([data-popper-placement]),
:deep(.date-picker-popup),
:deep(.calendar-popup),
:deep(.popover-content),
:deep(.dropdown-menu),
:deep(.v-calendar-popup),
:deep(.calendar-container),
:deep(.date-picker-container),
:deep([role="dialog"]),
:deep([data-radix-popper-content-wrapper]),
:deep([data-floating-ui-portal]),
:deep(.popover),
:deep(.dropdown-content),
:deep(.v-calendar-wrapper),
:deep(.date-picker-wrapper),
:deep(.calendar-dropdown),
:deep(.date-dropdown) {
    z-index: 2147483647 !important; /* Maximum z-index value (2^31 - 1) */
    position: fixed !important;
}

/* Target parent containers of popups */
:deep(div:has(.v-calendar)),
:deep(div:has(.v-date-picker)),
:deep(div:has([role="dialog"])) {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}
</style>
