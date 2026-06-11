<script setup lang="ts">
defineProps<{
    field: {
        label?: string;
    };
    inEditMode: boolean;
}>();

const emit = defineEmits<{
    "update:label": [value: string];
}>();
</script>

<template>
    <div class="w-full flex items-center gap-3 py-2">
        <div class="h-px flex-1 bg-outline-gray-2" />
        <input
            v-if="inEditMode"
            type="text"
            :value="field.label"
            @input="emit('update:label', ($event.target as HTMLInputElement).value)"
            class="bg-transparent border-none outline-none text-sm text-ink-gray-5 focus:ring-0 text-center px-0 py-0 min-w-20"
            placeholder="Step label"
            aria-label="Step label"
        />
        <span v-else class="text-sm text-ink-gray-5">{{ field.label }}</span>
        <div class="h-px flex-1 bg-outline-gray-2" />
    </div>
</template>
