<script setup lang="ts">
import draggableComponent from "vuedraggable";
import type { FormField } from "@/types/formfield";
import { ref, nextTick } from "vue";

const props = defineProps<{
    atRow: number;
    isDragging: boolean;
}>();

const emit = defineEmits<{
    drop: [field: FormField, atRow: number];
}>();

const buffer = ref<FormField[]>([]);

async function onZoneChange(evt: any) {
    if (evt.added) {
        emit("drop", evt.added.element, props.atRow);
        await nextTick();
        buffer.value = [];
    }
}
</script>

<template>
    <draggableComponent
        :list="buffer"
        :group="{ name: 'fields', put: true, pull: false }"
        item-key="fieldname"
        tag="div"
        :class="[
            'rounded transition-all duration-150',
            isDragging ? 'h-6 border-2 border-dashed border-gray-300 bg-gray-50' : 'h-1',
        ]"
        @change="onZoneChange"
    >
        <template #item="{}"></template>
    </draggableComponent>
</template>
