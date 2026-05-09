<script setup lang="ts">
import draggableComponent from "vuedraggable";
import type { FormField } from "@/types/formfield";
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";

const props = defineProps<{
    atRow: number;
    atCol: number;
    isDragging: boolean;
}>();

const emit = defineEmits<{
    drop: [field: FormField, atRow: number, atCol: number];
}>();

const buffer = ref<FormField[]>([]);
const draggableRef = ref<any>(null);
const isOver = ref(false);
let observer: MutationObserver | null = null;

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
        emit("drop", evt.added.element, props.atRow, props.atCol);
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
            'relative w-4 self-stretch',
            'before:content-[\'\'] before:absolute before:inset-y-0 before:left-1/2 before:-translate-x-1/2 before:rounded-full before:transition-all before:duration-150',
            isHighlighted
                ? 'before:w-1 before:bg-surface-blue-3'
                : isDragging
                ? 'before:w-px before:bg-surface-blue-1'
                : 'before:w-0 before:bg-transparent',
        ]"
        @change="onZoneChange"
    >
        <template #item="{}"></template>
    </draggableComponent>
</template>
