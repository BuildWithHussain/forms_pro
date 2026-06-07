<script setup lang="ts">
import { computed, ref } from "vue";
import { LoadingIndicator, TextEditor } from "frappe-ui";
import { onClickOutside, useEventListener } from "@vueuse/core";
import draggableComponent from "vuedraggable";

import { useEditForm } from "@/stores/editForm";
import { useGroupedRows } from "@/composables/useGroupedRows";
import type { FormField } from "@/types/formfield";
import FieldCard from "@/components/builder/FieldCard.vue";
import RowDropZone from "@/components/builder/RowDropZone.vue";
import ColumnDropZone from "@/components/builder/ColumnDropZone.vue";
import SectionNavBar from "@/components/builder/SectionNavBar.vue";

const editFormStore = useEditForm();

const fieldContentRef = ref<HTMLElement | null>(null);
const isDraggingField = ref(false);

function resetDragState() {
    isDraggingField.value = false;
}

useEventListener(document, "pointerup", () => {
    if (isDraggingField.value) resetDragState();
});
useEventListener(document, "dragend", () => {
    if (isDraggingField.value) resetDragState();
});

const groupedRows = useGroupedRows(
    computed(() =>
        editFormStore.isMultiSection ? editFormStore.activeSectionFields : editFormStore.fields
    )
);

function fieldKey(field: FormField): string {
    return `${field.row_index ?? 0}-${field.column_index ?? 0}-${field.cell_index ?? 0}`;
}

function rowIndexOf(row: FormField[][], rIdx: number): number {
    return row[0]?.[0]?.row_index ?? rIdx;
}

function colIndexOf(col: FormField[], cIdx: number): number {
    return col[0]?.column_index ?? cIdx;
}

function onCellChange(evt: any, rowIndex: number, colIndex: number) {
    if (evt.moved) {
        // Reorder cells within same column: renumber cell_index by new position
        const { element, newIndex } = evt.moved;
        const cells: FormField[] = editFormStore.fields
            .filter(
                (f: FormField) =>
                    (f.row_index ?? 0) === rowIndex && (f.column_index ?? 0) === colIndex
            )
            .sort((a: FormField, b: FormField) => (a.cell_index ?? 0) - (b.cell_index ?? 0));
        const oldIdx = cells.indexOf(element);
        if (oldIdx === -1) return;
        cells.splice(oldIdx, 1);
        cells.splice(newIndex, 0, element);
        cells.forEach((f: FormField, i: number) => {
            f.cell_index = i;
        });
    } else if (evt.added) {
        // Field dropped into this column from elsewhere — stack into column at cell index
        editFormStore.insertCell(evt.added.element, rowIndex, colIndex, evt.added.newIndex);
        resetDragState();
    }
    // evt.removed: no-op — target column's evt.added owns the move
}

function onColumnZoneDrop(field: FormField, atRow: number, atCol: number) {
    editFormStore.moveField(field, atRow, atCol);
    resetDragState();
}

function onRowZoneDrop(field: FormField, atRow: number) {
    editFormStore.insertNewRow(field, atRow);
    resetDragState();
}

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
    <div class="flex flex-col items-center flex-1 min-w-0">
        <div v-if="editFormStore.isLoading">
            <LoadingIndicator />
        </div>
        <SectionNavBar v-if="editFormStore.formData" class="max-w-screen-md w-full mt-6" />
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
            <div v-if="groupedRows.length === 0">
                <div
                    class="flex flex-col gap-2 p-4 min-h-24 items-center justify-center bg-gray-50 rounded text-center text-gray-500 border"
                >
                    <p class="text-base">Click on fields to add them to the form.</p>
                </div>
            </div>
            <div class="flex flex-col">
                <template v-for="(row, rIdx) in groupedRows" :key="rowIndexOf(row, rIdx)">
                    <RowDropZone
                        :atRow="rowIndexOf(row, rIdx)"
                        :isDragging="isDraggingField"
                        @drop="onRowZoneDrop"
                    />
                    <div
                        class="flex flex-row items-stretch"
                        data-form-builder-component="form-row"
                        :data-row-index="rowIndexOf(row, rIdx)"
                    >
                        <template
                            v-for="(col, cIdx) in row"
                            :key="`${rowIndexOf(row, rIdx)}-${colIndexOf(col, cIdx)}`"
                        >
                            <ColumnDropZone
                                :atRow="rowIndexOf(row, rIdx)"
                                :atCol="colIndexOf(col, cIdx)"
                                :isDragging="isDraggingField"
                                @drop="onColumnZoneDrop"
                            />
                            <draggableComponent
                                :list="[...col]"
                                :group="{ name: 'fields' }"
                                :item-key="fieldKey"
                                :animation="150"
                                handle=".handle"
                                ghost-class="opacity-50"
                                tag="div"
                                :force-fallback="true"
                                data-form-builder-component="cell-column"
                                :data-row-index="rowIndexOf(row, rIdx)"
                                :data-col-index="colIndexOf(col, cIdx)"
                                class="flex flex-col gap-4 flex-1 min-w-0"
                                @change="
                                (evt: any) =>
                                    onCellChange(
                                        evt,
                                        rowIndexOf(row, rIdx),
                                        colIndexOf(col, cIdx)
                                    )
                            "
                                @start="isDraggingField = true"
                                @end="isDraggingField = false"
                            >
                                <template #item="{ element: field }">
                                    <FieldCard
                                        :field="field"
                                        :isDraggingAnyField="isDraggingField"
                                    />
                                </template>
                            </draggableComponent>
                        </template>
                        <ColumnDropZone
                            :atRow="rowIndexOf(row, rIdx)"
                            :atCol="row.length"
                            :isDragging="isDraggingField"
                            @drop="onColumnZoneDrop"
                        />
                    </div>
                    <RowDropZone
                        v-show="rIdx === groupedRows.length - 1"
                        :atRow="rowIndexOf(row, rIdx) + 1"
                        :isDragging="isDraggingField"
                        @drop="onRowZoneDrop"
                    />
                </template>
            </div>
        </div>
    </div>
</template>
