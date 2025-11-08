<script setup lang="ts">
import draggableComponent from "vuedraggable";
import { LoadingIndicator, TextEditor } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { GripVertical } from "lucide-vue-next";
import { FormField } from "@/types/formfield";
import { ref, computed } from "vue";
import { onClickOutside } from "@vueuse/core";

import FieldRenderer from "@/components/builder/FieldRenderer.vue";
import Button from "frappe-ui/src/components/Button/Button.vue";

const editFormStore = useEditForm();

// Helper function to get image URL
const getImageUrl = (filePath: string | null | undefined): string => {
    if (!filePath) {
        console.log('[FormBuilderContent] getImageUrl: No file path provided');
        return '';
    }
    
    console.log('[FormBuilderContent] getImageUrl: Input path:', filePath);
    
    // If it's already a full URL, return as is
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        console.log('[FormBuilderContent] getImageUrl: Full URL detected');
        return filePath;
    }
    
    // If it already starts with /files/, return as is
    if (filePath.startsWith('/files/')) {
        console.log('[FormBuilderContent] getImageUrl: /files/ prefix detected');
        return filePath;
    }
    
    // If it starts with "files/" (without leading slash), remove it first
    let cleanPath = filePath;
    if (cleanPath.startsWith('files/')) {
        cleanPath = cleanPath.substring(6); // Remove 'files/'
        console.log('[FormBuilderContent] getImageUrl: Removed "files/" prefix, clean path:', cleanPath);
    }
    
    // Remove leading slash if present
    if (cleanPath.startsWith('/')) {
        cleanPath = cleanPath.substring(1);
    }
    
    // Construct the URL
    const finalUrl = `/files/${cleanPath}`;
    console.log('[FormBuilderContent] getImageUrl: Constructed URL:', finalUrl);
    return finalUrl;
};

// Computed styles for real-time preview background - matching SubmissionPage exactly
const previewStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData) {
        console.log('[FormBuilderContent] previewStyles: No form data');
        return {};
    }
    
    const styles: Record<string, string> = {};
    
    // Background image - convert file path to URL like the API does
    if (formData.background_image) {
        console.log('[FormBuilderContent] previewStyles: Background image found:', formData.background_image);
        
        // Convert file path to URL (same as backend API does with frappe.utils.get_url)
        let imageUrl = formData.background_image;
        
        // If it's not already a full URL, convert it
        if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
            // Convert to /files/ URL format
            imageUrl = getImageUrl(imageUrl);
        }
        
        console.log('[FormBuilderContent] previewStyles: Final image URL:', imageUrl);
        
        styles.backgroundImage = `url(${imageUrl})`;
        styles.backgroundSize = 'cover';
        styles.backgroundPosition = 'center';
        styles.backgroundRepeat = 'no-repeat';
        styles.backgroundAttachment = 'fixed';
    } else {
        console.log('[FormBuilderContent] previewStyles: No background image');
    }
    
    // Background color (fallback or solid) - same logic as SubmissionPage
    if (formData.background_color) {
        if (!formData.background_image) {
            styles.backgroundColor = formData.background_color;
        }
    } else if (!formData.background_image) {
        styles.backgroundColor = '#f9fafb';
    }
    
    console.log('[FormBuilderContent] previewStyles: Final styles:', styles);
    return styles;
});

// Overlay styles for background
const overlayStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData || !formData.background_image) return {};
    
    const opacity = formData.overlay_opacity || 0.5;
    return {
        backgroundColor: `rgba(0, 0, 0, ${opacity * 0.4})`
    };
});

const containerStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData) return {};
    
    const styles: Record<string, string> = {};
    
    // Glass morphism effect
    // NOTE: backdrop-filter creates a stacking context, so we need to be careful
    // We'll apply it but ensure popups can escape via JavaScript
    if (formData.glass_morphism_enabled) {
        styles.backdropFilter = 'blur(10px) saturate(180%)';
        styles.webkitBackdropFilter = 'blur(10px) saturate(180%)';
        styles.backgroundColor = 'rgba(255, 255, 255, 0.75)';
        styles.border = '1px solid rgba(255, 255, 255, 0.3)';
        styles.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.2)';
        // Ensure z-index is low so popups can appear above
        styles.zIndex = '1';
    } else {
        styles.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        styles.border = '1px solid rgba(0, 0, 0, 0.1)';
        styles.boxShadow = '0 4px 16px 0 rgba(0, 0, 0, 0.1)';
        styles.zIndex = '1';
    }
    
    // Overlay opacity adjustment
    if (formData.overlay_opacity !== undefined) {
        const opacity = formData.overlay_opacity;
        if (formData.glass_morphism_enabled) {
            styles.backgroundColor = `rgba(255, 255, 255, ${0.75 * opacity})`;
        }
    }
    
    return styles;
});

const themeColor = computed(() => {
    return editFormStore.formData?.theme_color || '#3b82f6';
});

// Font family for form
const fontFamily = computed(() => {
    const font = editFormStore.formData?.font_family || 'System Default';
    if (font === 'System Default') {
        return '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    }
    return font;
});

// Logo URL - get from formData and convert to proper URL
const logoUrl = computed(() => {
    const logo = editFormStore.formData?.logo;
    if (!logo) {
        console.log('[FormBuilderContent] logoUrl: No logo in formData');
        return null;
    }
    console.log('[FormBuilderContent] logoUrl: Logo found:', logo);
    const url = getImageUrl(logo);
    console.log('[FormBuilderContent] logoUrl: Constructed URL:', url);
    return url;
});

// Ref for the entire FormBuilderContent component
const fieldContentRef = ref<HTMLElement | null>(null);

// Set up outside click detection for the entire FormBuilderContent component
onClickOutside(fieldContentRef, (event) => {
    // Check if the click is on any other form builder components
    const target = event.target as Element;
    const isFormBuilderComponent =
        target.closest("[data-form-builder-component]") ||
        target.closest(".field-editor-sidebar") ||
        target.closest(".form-builder-sidebar") ||
        target.closest(".form-builder-header");

    // Only deselect if NOT clicking on other form builder components
    if (!isFormBuilderComponent) {
        editFormStore.selectField(null);
    }
});
</script>
<template>
    <div v-if="editFormStore.isLoading">
        <LoadingIndicator />
    </div>
    <!-- Background container - matches SubmissionPage structure exactly -->
    <div
        v-if="editFormStore.formData"
        class="min-h-screen relative flex-1"
        :style="previewStyles"
    >
        <!-- Overlay for background -->
        <div
            v-if="editFormStore.formData.background_image"
            class="absolute inset-0 z-0"
            :style="overlayStyles"
        ></div>
        
        <!-- Main content - matches SubmissionPage -->
        <div class="relative min-h-screen p-8" style="z-index: 1;">
            <div
                class="space-y-4 rounded-lg p-6 max-w-screen-md mx-auto mt-16 transition-all duration-300 form-container"
                :style="{ ...containerStyles, fontFamily: fontFamily }"
                style="z-index: 1; position: relative;"
            >
        <div class="flex flex-col gap-2">
            <div class="flex items-start justify-between gap-4">
                <input
                    type="text"
                    class="outline-none bg-transparent border-none text-3xl font-semibold focus:ring-0 p-2 flex-1"
                    placeholder="Untitled Form"
                    v-model="editFormStore.formData.title"
                />
                <img 
                    v-if="logoUrl"
                    :src="logoUrl"
                    alt="Logo"
                    class="max-w-[150px] max-h-[60px] object-contain"
                    style="flex-shrink: 0;"
                />
            </div>
            <TextEditor
                :model-value="editFormStore.formData.description"
                editor-class="h-fit !w-full p-2 form-description"
                placeholder="Write a description for your form"
                @change="(value: string) => (editFormStore.formData.description = value)"
                :starterkit-options="{
                    heading: {
                        levels: [2, 3, 4, 5, 6],
                    },
                }"
            />
        </div>
        <hr class="my-4" />
        <div v-if="editFormStore.fields.length === 0">
            <div
                class="flex flex-col gap-2 p-4 min-h-24 items-center justify-center bg-gray-50 rounded text-center text-gray-500 border"
            >
                <p class="text-base">Click on fields to add them to the form.</p>
            </div>
        </div>
        <div>
            <draggableComponent :list="editFormStore.fields" item-key="idx" tag="div">
                <template #item="{ element }">
                    <div
                        ref="fieldContentRef"
                        @click="editFormStore.selectField(element)"
                        :class="{ 'border-gray-400': editFormStore.selectedField === element }"
                        class="p-2 my-3 bg-gray-50 rounded border flex gap-2 relative transition-colors"
                    >
                        <GripVertical class="w-4 h-4 handle" />
                        <FieldRenderer
                            :field="element"
                            @update:field="
                                (updatedField: FormField) =>
                                    editFormStore.updateField(element, updatedField)
                            "
                            :inEditMode="true"
                            :theme-color="themeColor"
                        />
                        <Button
                            icon="x"
                            variant="outline"
                            class="absolute -top-2 -right-2"
                            @click="editFormStore.removeField(element)"
                        />
                    </div>
                </template>
            </draggableComponent>
        </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.handle {
    cursor: grab;
}

/* Form container should have low z-index - DO NOT use isolation as it traps popups */
/* Also ensure it doesn't create a stacking context that traps children */
.form-container {
    position: relative;
    z-index: 1 !important;
    /* Removed isolation: isolate - it creates a stacking context that traps popups */
    /* Ensure transform and opacity don't create stacking context */
    transform: none !important;
    opacity: 1 !important;
}

/* Ensure all popups (date pickers, dropdowns, etc.) appear above the form container */
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
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}

/* Ensure form field popups are above everything */
:deep(.form-field-popup) {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}
</style>

<style>
/* Global styles - ensure ALL popups are above form container with maximum z-index */
/* Use body selector for maximum specificity */
body .v-calendar,
body .v-date-picker,
body .v-popover,
body .v-dropdown,
body .v-menu,
body [data-popper-placement],
body .date-picker-popup,
body .calendar-popup,
body .popover-content,
body .dropdown-menu,
body .frappe-ui-date-picker-popup,
body .frappe-ui-dropdown-popup,
body .v-calendar-popup,
body .calendar-container,
body .date-picker-container,
body .v-calendar-wrapper,
body .date-picker-wrapper,
body .calendar-dropdown,
body .date-dropdown {
    z-index: 2147483647 !important; /* Maximum z-index value (2^31 - 1) */
    position: fixed !important;
}

/* Ensure date picker calendar appears in front - target all possible structures */
body div[role="dialog"],
body div[data-radix-popper-content-wrapper],
body div[data-floating-ui-portal],
body div[data-floating-ui-root],
body .popover,
body .dropdown-content,
body [data-headlessui-portal],
body [data-radix-portal],
body [data-floating-ui-root] {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}

/* Target any element that contains calendar/date picker classes */
body div:has(.v-calendar),
body div:has(.v-date-picker),
body div:has(.calendar),
body div:has([role="dialog"]),
body div:has([data-popper-placement]) {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}

/* Very aggressive - target any fixed/absolute positioned element that might be a popup */
body > div[style*="position: fixed"],
body > div[style*="position:absolute"] {
    z-index: 2147483647 !important; /* Maximum z-index value */
}

/* Target Frappe UI specific popup structures */
body .frappe-ui-popup,
body .frappe-ui-modal,
body .frappe-ui-overlay {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}

/* Nuclear option - any element with calendar/date in class name or data attribute */
[class*="calendar"],
[class*="date-picker"],
[class*="datepicker"],
[data-calendar],
[data-date-picker],
[data-datepicker] {
    z-index: 2147483647 !important; /* Maximum z-index value */
    position: fixed !important;
}

/* Ensure form container and its children have low z-index */
.form-container,
.form-container * {
    position: relative;
    z-index: auto !important;
}

/* Exception: popups inside form container should break out */
.form-container [role="dialog"],
.form-container [data-popper-placement],
.form-container .v-calendar,
.form-container .v-date-picker,
.form-container .popover,
.form-container .dropdown-menu {
    position: fixed !important;
    z-index: 2147483647 !important; /* Maximum z-index value */
}
</style>
