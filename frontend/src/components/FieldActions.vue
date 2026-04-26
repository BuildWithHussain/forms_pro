<script setup lang="ts">
import { GripVertical, Trash2 } from "@lucide/vue";
import { Button } from "frappe-ui";

defineProps<{
    isSelected: boolean;
}>();

defineEmits<{
    (e: "remove"): void;
}>();
</script>
<template>
    <div
        :class="[
            'absolute right-full top-2 mr-2 flex flex-row items-center rounded border bg-surface-white px-1 h-8 transition-all duration-200 ease-out ',
            isSelected
                ? 'opacity-100 scale-100'
                : 'opacity-0 scale-80 group-hover:opacity-100 group-hover:scale-100',
        ]"
    >
        <Button size="sm" :icon="Trash2" variant="ghost" @click.stop="$emit('remove')" />
        <Button size="sm" :icon="GripVertical" variant="ghost" />
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
