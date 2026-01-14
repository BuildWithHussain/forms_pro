<script setup lang="ts">
import { useEditForm } from "@/stores/editForm";
import FieldPropertiesForm from "@/components/builder/field-editor/FieldPropertiesForm.vue";

const editFormStore = useEditForm();
</script>
<template>
    <div
        class="field-editor-sidebar h-[calc(100vh-3rem)] w-72 border-l sticky top-0 overflow-y-auto flex"
        data-form-builder-component="field-editor-sidebar"
    >
        <div v-if="!editFormStore.selectedField">
            <div
                class="flex flex-col gap-2 p-4 h-full items-center justify-center text-center bg-gray-50 rounded m-2"
            >
                <h3 class="text-base font-medium text-gray-600">
                    Select a field to edit its properties.
                </h3>
            </div>
        </div>
        <div class="w-full" v-else>
            <FieldPropertiesForm v-model="editFormStore.selectedField" />
        </div>
    </div>
</template>
