<script setup lang="ts">
import draggableComponent from "vuedraggable";
import type { FormField } from "@/types/formfield";
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";

const props = defineProps<{
    atRow: number;
    isDragging: boolean;
}>();

const emit = defineEmits<{
    drop: [field: FormField, atRow: number];
}>();

const buffer = ref<FormField[]>([]);
const draggableRef = ref<any>(null);
const isOver = ref(false);
let observer: MutationObserver | null = null;

// SortableJS inserts a placeholder child into the target list while hovering.
// Watching for that insertion is more reliable than pointer events during drag.
onMounted(() => {
    const el = draggableRef.value?.$el;
    if (!el) return;
    observer = new MutationObserver(() => {
        isOver.value = el.children.length > 0;
    });
    observer.observe(el, { childList: true });
});

onUnmounted(() => {
    observer?.disconnect();
});

const isHighlighted = computed(() => props.isDragging && isOver.value);

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
        ref="draggableRef"
        :list="buffer"
        :group="{ name: 'fields', put: true, pull: false }"
        item-key="fieldname"
        tag="div"
        :class="[
            'relative h-6 w-full',
            'before:content-[\'\'] before:absolute before:inset-x-0 before:top-1/2 before:-translate-y-1/2 before:rounded-full before:transition-all before:duration-150',
            isHighlighted
                ? 'before:h-1 before:bg-surface-blue-3'
                : isDragging
                ? 'before:h-px before:bg-surface-blue-1'
                : 'before:h-0 before:bg-transparent',
        ]"
        @change="onZoneChange"
    >
        <template #item="{}"></template>
    </draggableComponent>
</template>
