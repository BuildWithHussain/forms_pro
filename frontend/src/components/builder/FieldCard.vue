<script setup lang="ts">
import type { FormField } from "@/types/formfield";
import { useEditForm } from "@/stores/editForm";
import FieldActions from "@/components/builder/FieldActions.vue";
import FieldRenderer from "@/components/builder/FieldRenderer.vue";

const props = defineProps<{
    field: FormField;
    isDraggingAnyField: boolean;
}>();

const editFormStore = useEditForm();
</script>

<template>
    <div
        class="relative flex-1 min-w-0 transition-colors group"
        @click="editFormStore.selectField(props.field)"
    >
        <FieldActions
            :isSelected="editFormStore.selectedField === props.field"
            :isDraggingAnyField="props.isDraggingAnyField"
            @remove="editFormStore.removeField(props.field)"
        />
        <FieldRenderer
            :field="props.field"
            :inEditMode="true"
            @update:field="
                (updated: FormField) => editFormStore.updateField(props.field, updated)
            "
        />
    </div>
</template>
