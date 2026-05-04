<script setup lang="ts">
import { computed, ref } from "vue";
import { LoadingIndicator, TextEditor } from "frappe-ui";
import { onClickOutside, useEventListener } from "@vueuse/core";

import { useEditForm } from "@/stores/editForm";
import { useGroupedRows } from "@/composables/useGroupedRows";
import FieldCard from "@/components/builder/FieldCard.vue";

const editFormStore = useEditForm();

const fieldContentRef = ref<HTMLElement | null>(null);
const isDraggingField = ref(false);

const groupedRows = useGroupedRows(computed(() => editFormStore.fields));

// Function to check if an element is a dropdown/popover (including portals)
const isDropdownOrPopover = (element: Element | null): boolean => {
    if (!element) return false;

    let current: Element | null = element;
    while (current && current !== document.body) {
        if (
            current.hasAttribute("role") &&
            (current.getAttribute("role") === "listbox" ||
                current.getAttribute("role") === "option" ||
                current.getAttribute("role") === "combobox")
        ) {
            return true;
        }

        if (current.hasAttribute("data-headlessui-state") || current.id?.includes("headlessui")) {
            return true;
        }

        if (
            current.hasAttribute("data-radix-popper-content-wrapper") ||
            current.id?.startsWith("radix") ||
            current.hasAttribute("data-radix")
        ) {
            return true;
        }

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

useEventListener("keydown", (event: KeyboardEvent) => {
    if (event.metaKey && event.key === "s") {
        event.preventDefault();
        editFormStore.save();
    }
});

onClickOutside(fieldContentRef, (event) => {
    const target = event.target as Element;
    const isFormBuilderComponent =
        target.closest("[data-form-builder-component]") ||
        target.closest(".field-editor-sidebar") ||
        target.closest(".form-builder-sidebar") ||
        target.closest(".form-builder-header");

    const isDropdownElement = isDropdownOrPopover(target);

    const hasOpenDropdown = !!(
        document.querySelector('[role="listbox"]:not([hidden]):not([style*="display: none"])') ||
        document.querySelector('[role="combobox"][aria-expanded="true"]') ||
        document.querySelector('[data-headlessui-state="open"]') ||
        document.querySelector('[aria-expanded="true"][role="combobox"]')
    );

    const activeElement = document.activeElement;
    const isActiveElementInSidebar = activeElement
        ? !!(
              activeElement.closest(".field-editor-sidebar") ||
              activeElement.closest('[data-form-builder-component="field-editor-sidebar"]') ||
              activeElement.closest('[data-form-builder-component="field-properties-form"]')
          )
        : false;

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
        <div class="flex flex-col gap-2">
            <div
                v-for="(row, rIdx) in groupedRows"
                :key="rIdx"
                class="flex flex-row gap-2 items-stretch"
            >
                <FieldCard
                    v-for="field in row"
                    :key="field.idx"
                    :field="field"
                    :isDraggingAnyField="isDraggingField"
                />
            </div>
        </div>
    </div>
</template>
