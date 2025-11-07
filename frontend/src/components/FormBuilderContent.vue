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
    if (!filePath) return '';
    // If it's already a full URL, return as is
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        return filePath;
    }
    // If it already starts with /files/, return as is
    if (filePath.startsWith('/files/')) {
        return filePath;
    }
    // Otherwise, construct the URL using Frappe's file URL format
    const cleanPath = filePath.startsWith('/') ? filePath.substring(1) : filePath;
    return `/files/${cleanPath}`;
};

// Computed styles for real-time preview background - matching SubmissionPage exactly
const previewStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData) return {};
    
    const styles: Record<string, string> = {};
    
    // Background image - convert file path to URL like the API does
    if (formData.background_image) {
        // Convert file path to URL (same as backend API does with frappe.utils.get_url)
        let imageUrl = formData.background_image;
        
        // If it's not already a full URL, convert it
        if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
            // Convert to /files/ URL format
            imageUrl = getImageUrl(imageUrl);
        }
        
        styles.backgroundImage = `url(${imageUrl})`;
        styles.backgroundSize = 'cover';
        styles.backgroundPosition = 'center';
        styles.backgroundRepeat = 'no-repeat';
        styles.backgroundAttachment = 'fixed';
    }
    
    // Background color (fallback or solid) - same logic as SubmissionPage
    if (formData.background_color) {
        if (!formData.background_image) {
            styles.backgroundColor = formData.background_color;
        }
    } else if (!formData.background_image) {
        styles.backgroundColor = '#f9fafb';
    }
    
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
    if (formData.glass_morphism_enabled) {
        styles.backdropFilter = 'blur(10px) saturate(180%)';
        styles.webkitBackdropFilter = 'blur(10px) saturate(180%)';
        styles.backgroundColor = 'rgba(255, 255, 255, 0.75)';
        styles.border = '1px solid rgba(255, 255, 255, 0.3)';
        styles.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.2)';
    } else {
        styles.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        styles.border = '1px solid rgba(0, 0, 0, 0.1)';
        styles.boxShadow = '0 4px 16px 0 rgba(0, 0, 0, 0.1)';
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
        <div class="relative z-10 min-h-screen p-8">
            <div
                class="space-y-4 rounded-lg p-6 max-w-screen-md mx-auto mt-16 transition-all duration-300"
                :style="containerStyles"
            >
        <div class="flex flex-col gap-2">
            <input
                type="text"
                class="outline-none bg-transparent border-none text-3xl font-semibold focus:ring-0 p-2"
                placeholder="Untitled Form"
                v-model="editFormStore.formData.title"
            />
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
</style>
