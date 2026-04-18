<script setup lang="ts">
import { computed } from "vue";
import { Checkbox } from "frappe-ui";

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

function toggle(option: string, checked: boolean) {
    if (checked) {
        selected.value = [...selected.value, option];
    } else {
        selected.value = selected.value.filter((v) => v !== option);
    }
}
</script>

<template>
    <div class="flex flex-col gap-1">
        <label
            v-for="option in options"
            :key="option"
            class="flex items-center gap-2 min-h-[32px] rounded px-1 cursor-pointer hover:bg-surface-gray-2 active:bg-surface-gray-3 transition"
            :class="{ 'opacity-50 cursor-not-allowed': disabled }"
        >
            <Checkbox
                :modelValue="selected.includes(option)"
                :disabled="disabled"
                size="sm"
                @update:modelValue="toggle(option, $event)"
            />
            <span class="text-base text-ink-gray-8 select-none">{{ option }}</span>
        </label>
        <span v-if="!options?.length" class="text-sm text-ink-gray-4 italic">
            No options defined
        </span>
    </div>
</template>
