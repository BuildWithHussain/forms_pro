<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
    options?: string[];
    disabled?: boolean;
}>();

const modelValue = defineModel<string[]>({ default: () => [] });

const selected = computed({
    get() {
        return Array.isArray(modelValue.value) ? modelValue.value : [];
    },
    set(val: string[]) {
        modelValue.value = val;
    },
});

function toggle(option: string) {
    if (props.disabled) return;
    const current = selected.value;
    if (current.includes(option)) {
        selected.value = current.filter((v) => v !== option);
    } else {
        selected.value = [...current, option];
    }
}
</script>

<template>
    <div class="flex flex-col gap-2">
        <label
            v-for="option in options"
            :key="option"
            class="flex items-center gap-2 cursor-pointer"
            :class="{ 'opacity-50 cursor-not-allowed': disabled }"
        >
            <input
                type="checkbox"
                :value="option"
                :checked="selected.includes(option)"
                :disabled="disabled"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                @change="toggle(option)"
            />
            <span class="text-sm text-ink-gray-7">{{ option }}</span>
        </label>
        <span v-if="!options?.length" class="text-sm text-ink-gray-4 italic">
            No options defined
        </span>
    </div>
</template>
