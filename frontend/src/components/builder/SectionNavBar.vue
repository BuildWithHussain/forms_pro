<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import { Plus, CircleCheck, X } from "@lucide/vue";
import { Button, TextInput } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { dialog } from "@/utils/dialog";

const store = useEditForm();

const sectionCount = computed(() => store.sections.length);
const editingIndex = ref<number | null>(null);
const editInput = ref<InstanceType<typeof TextInput> | null>(null);
const editValue = ref("");
const cancelRename = ref(false);

function startRename(index: number) {
    editValue.value = store.sections[index].label;
    editingIndex.value = index;
    nextTick(() => editInput.value?.el?.select());
}

function finishRename(index: number) {
    if (cancelRename.value) {
        cancelRename.value = false;
        editingIndex.value = null;
        return;
    }
    if (editValue.value.trim()) {
        store.renameStep(index, editValue.value.trim());
    }
    editingIndex.value = null;
}

function onEditKeydown(event: KeyboardEvent, index: number) {
    if (event.key === "Enter") {
        finishRename(index);
    } else if (event.key === "Escape") {
        cancelRename.value = true;
        editingIndex.value = null;
    }
}

function confirmRemoveSection(index: number) {
    const section = store.sections[index];
    const hasFields = section.fields.length > 0;

    if (!hasFields) {
        store.removeStepKeepFields(index);
        return;
    }

    dialog.show({
        title: `Remove "${section.label}"?`,
        message: `This step has ${section.fields.length} field(s). What would you like to do?`,
        actions: [
            {
                label: "Cancel",
                variant: "outline",
                onClick: () => dialog.close(false),
            },
            {
                label: "Move fields to previous step",
                variant: "subtle",
                onClick: () => {
                    store.removeStepKeepFields(index);
                    dialog.close(true);
                },
            },
            {
                label: "Remove step and fields",
                variant: "solid",
                theme: "red",
                onClick: () => {
                    store.removeStepWithFields(index);
                    dialog.close(true);
                },
            },
        ],
    });
}
</script>

<template>
    <nav aria-label="Form steps" class="flex items-center gap-1.5 px-2 py-1.5 flex-wrap">
        <template v-if="sectionCount <= 1">
            <Button
                variant="ghost"
                size="sm"
                label="Add Step"
                :icon-left="Plus"
                aria-label="Add Step"
                tooltip="Click to add a new step to the form"
                @click="store.addStep()"
            />
        </template>
        <template v-else>
            <template v-for="(section, idx) in store.sections" :key="section.label">
                <Button
                    v-if="editingIndex !== idx"
                    :variant="idx === store.activeSectionIndex ? 'outline' : 'ghost'"
                    size="sm"
                    :label="section.label"
                    :aria-current="idx === store.activeSectionIndex ? 'true' : undefined"
                    @click="store.activeSectionIndex = idx"
                    @dblclick="startRename(idx)"
                    tooltip="Double-click to rename"
                    :class="{
                        'shadow-sm': idx === store.activeSectionIndex,
                    }"
                >
                    <template v-if="idx > 0" #suffix>
                        <X
                            class="w-3 h-3 text-ink-gray-4 hover:text-ink-gray-7 rounded-sm"
                            role="button"
                            aria-label="Remove step"
                            @click.stop="confirmRemoveSection(idx)"
                        />
                    </template>
                </Button>
                <TextInput
                    v-else
                    ref="editInput"
                    v-model="editValue"
                    size="sm"
                    variant="outline"
                    @blur="finishRename(idx)"
                    @keydown="onEditKeydown($event, idx)"
                    class="w-fit"
                />
                <span
                    v-if="idx < store.sections.length - 1"
                    class="w-1 h-1 rounded-full bg-outline-gray-3"
                />
            </template>
            <span class="w-1 h-1 rounded-full bg-outline-gray-3" />
            <Button
                variant="ghost"
                size="sm"
                label="Add Step"
                :icon="Plus"
                aria-label="Add Step"
                tooltip="Click to add a new step to the form"
                @click="store.addStep()"
            />
        </template>
        <span class="w-1 h-1 rounded-full bg-outline-gray-3" />
        <span class="flex items-center gap-1.5 text-sm text-ink-gray-4">
            <CircleCheck class="w-4 h-4" />
            Success
        </span>
    </nav>
</template>
