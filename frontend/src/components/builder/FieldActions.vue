<script setup lang="ts">
import { GripVertical, SquareSplitVertical, Trash2 } from "@lucide/vue";
import { Button } from "frappe-ui";

defineProps<{
    isSelected: boolean;
    isDraggingAnyField: boolean;
    isMultiColumn: boolean;
}>();

defineEmits<{
    (e: "remove"): void;
    (e: "eject"): void;
}>();
</script>
<template>
    <div
        :class="[
            'absolute right-full top-2 mr-2 flex flex-row items-center rounded border bg-surface-white px-1 h-8 transition-all duration-200 ease-out ',
            isSelected
                ? 'opacity-100 scale-100'
                : isDraggingAnyField
                ? 'opacity-0 scale-90 pointer-events-none'
                : 'opacity-0 scale-90 group-hover:opacity-100 group-hover:scale-100',
        ]"
    >
        <Button
            v-if="isMultiColumn"
            size="sm"
            :icon="SquareSplitVertical"
            variant="ghost"
            @click.stop="$emit('eject')"
            tooltip="Move to own row"
            data-form-builder-component="eject-button"
        />
        <Button
            size="sm"
            :icon="Trash2"
            variant="ghost"
            @click.stop="$emit('remove')"
            tooltip="Remove this field"
        />
        <Button
            class="handle"
            size="sm"
            :icon="GripVertical"
            variant="ghost"
            tooltip="Drag to move"
        />
    </div>
</template>

<style scoped>
.handle {
    cursor: grab;
}

.handle:active {
    cursor: grabbing;
}
</style>
