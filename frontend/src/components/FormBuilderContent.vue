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

// Computed styles for real-time preview
const previewStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData) return {};
    
    const styles: Record<string, string> = {};
    
    // Background image
    if (formData.background_image) {
        styles.backgroundImage = `url(${formData.background_image})`;
        styles.backgroundSize = 'cover';
        styles.backgroundPosition = 'center';
        styles.backgroundRepeat = 'no-repeat';
    }
    
    // Background color (fallback if no image)
    if (formData.background_color) {
        styles.backgroundColor = formData.background_color;
    }
    
    return styles;
});

const containerStyles = computed(() => {
    const formData = editFormStore.formData;
    if (!formData) return {};
    
    const styles: Record<string, string> = {};
    
    // Glass morphism effect
    if (formData.glass_morphism_enabled) {
        styles.backdropFilter = 'blur(10px)';
        styles.backgroundColor = 'rgba(255, 255, 255, 0.7)';
        styles.border = '1px solid rgba(255, 255, 255, 0.3)';
        styles.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.37)';
    }
    
    // Overlay opacity
    if (formData.overlay_opacity !== undefined && formData.overlay_opacity > 0) {
        const opacity = formData.overlay_opacity;
        if (formData.glass_morphism_enabled) {
            styles.backgroundColor = `rgba(255, 255, 255, ${0.7 * opacity})`;
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
    <div
        v-if="editFormStore.formData"
        class="min-h-[800px] max-w-screen-md w-full border rounded my-12 p-4 relative overflow-hidden"
        :style="previewStyles"
    >
        <!-- Overlay for background -->
        <div
            v-if="editFormStore.formData.background_image && editFormStore.formData.overlay_opacity"
            class="absolute inset-0 z-0"
            :style="{
                backgroundColor: `rgba(0, 0, 0, ${(editFormStore.formData.overlay_opacity || 0.5) * 0.3})`
            }"
        ></div>
        
        <!-- Form content container with glass morphism -->
        <div
            class="relative z-10"
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
</template>

<style scoped>
.handle {
    cursor: grab;
}
</style>
