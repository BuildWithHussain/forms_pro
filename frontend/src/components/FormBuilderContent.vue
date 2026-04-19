<script setup lang="ts">
import draggableComponent from "vuedraggable";
import { LoadingIndicator, TextEditor, Button } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { GripVertical } from "lucide-vue-next";
import { FormField } from "@/types/formfield";
import { ref } from "vue";
import { onClickOutside } from "@vueuse/core";

import FieldRenderer from "@/components/builder/FieldRenderer.vue";

const editFormStore = useEditForm();

// Ref for the entire FormBuilderContent component
const fieldContentRef = ref<HTMLElement | null>(null);

// Function to check if an element is a dropdown/popover (including portals)
const isDropdownOrPopover = (element: Element | null): boolean => {
    if (!element) return false;

    // Walk up the DOM tree to check for dropdown indicators
    let current: Element | null = element;
    while (current && current !== document.body) {
        // Check for Headless UI patterns
        if (
            current.hasAttribute("role") &&
            (current.getAttribute("role") === "listbox" ||
                current.getAttribute("role") === "option" ||
                current.getAttribute("role") === "combobox")
        ) {
            return true;
        }

        // Check for Headless UI data attributes
        if (current.hasAttribute("data-headlessui-state") || current.id?.includes("headlessui")) {
            return true;
        }

        // Check for Radix UI patterns
        if (
            current.hasAttribute("data-radix-popper-content-wrapper") ||
            current.id?.startsWith("radix") ||
            current.hasAttribute("data-radix")
        ) {
            return true;
        }

        // Check for common dropdown classes
        const classList = current.classList;
        if (
            classList.contains("dropdown-menu") ||
            classList.contains("combobox-options") ||
            classList.contains("popover-content") ||
            current.hasAttribute("data-popover")
        ) {
            return true;
        }

        current = current.parentElement;
    }

    return false;
};

// Set up outside click detection for the entire FormBuilderContent component
onClickOutside(fieldContentRef, (event) => {
    // Check if the click is on any other form builder components
    const target = event.target as Element;
    const isFormBuilderComponent =
        target.closest("[data-form-builder-component]") ||
        target.closest(".field-editor-sidebar") ||
        target.closest(".form-builder-sidebar") ||
        target.closest(".form-builder-header");

    // Check if the click is on a dropdown menu (which may be rendered in a portal)
    // This handles Headless UI, Radix UI, and other common dropdown patterns
    const isDropdownElement = isDropdownOrPopover(target);

    // Also check if there are any visible/open dropdowns in the DOM
    // This catches dropdowns that might be open but the click target isn't directly on them
    const hasOpenDropdown = !!(
        document.querySelector('[role="listbox"]:not([hidden]):not([style*="display: none"])') ||
        document.querySelector('[role="combobox"][aria-expanded="true"]') ||
        document.querySelector('[data-headlessui-state="open"]') ||
        document.querySelector('[aria-expanded="true"][role="combobox"]')
    );

    // Check if the active element (focused element) is within the sidebar
    // This helps catch cases where a dropdown is open and the user is interacting with it
    const activeElement = document.activeElement;
    const isActiveElementInSidebar = activeElement
        ? !!(
              activeElement.closest(".field-editor-sidebar") ||
              activeElement.closest('[data-form-builder-component="field-editor-sidebar"]') ||
              activeElement.closest('[data-form-builder-component="field-properties-form"]')
          )
        : false;

    // Only deselect if NOT clicking on other form builder components or dropdowns
    // Also don't deselect if there's an open dropdown or if the active element is in the sidebar
    if (
        !isFormBuilderComponent &&
        !isDropdownElement &&
        !hasOpenDropdown &&
        !isActiveElementInSidebar
    ) {
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
        ref="fieldContentRef"
        class="bg-secondary min-h-[800px] max-w-screen-md w-full border rounded my-12 p-4 shadow-[0_0_10px_rgba(0,0,0,0.1)]"
    >
        <div class="flex flex-col gap-2">
            <input
                type="text"
                class="outline-none bg-transparent border-none text-3xl font-semibold focus:ring-0 p-2"
                placeholder="Untitled Form"
                v-model="editFormStore.formData.title"
            />
            <TextEditor
                :content="editFormStore.formData.description"
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
</template>

<style scoped>
.handle {
    cursor: grab;
}
</style>
