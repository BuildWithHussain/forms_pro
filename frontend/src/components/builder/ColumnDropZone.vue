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
            'transition-all duration-150 self-stretch',
            isHighlighted
                ? 'bg-surface-blue-3 w-1'
                : isDragging
                ? 'bg-surface-blue-1 w-1'
                : 'bg-transparent w-px',
        ]"
        @change="onZoneChange"
    >
        <template #item="{}"></template>
    </draggableComponent>
</template>
