<script setup lang="ts">
import { computed } from "vue";
import { Button, Checkbox } from "frappe-ui";

const props = defineProps<{
    options?: string[];
    disabled?: boolean;
    inEditMode?: boolean;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    field?: Record<string, any>;
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

function removeOption(option: string) {
    if (!props.field) return;
    const items = (props.field.options ?? "").split("\n").filter(Boolean);
    props.field.options = items.filter((v: string) => v !== option).join("\n");
    selected.value = selected.value.filter((v) => v !== option);
}
</script>

<template>
    <div class="flex flex-col gap-1">
        <div
            v-for="option in options"
            :key="option"
            class="flex items-center gap-2 min-h-[32px] rounded px-1 transition"
            :class="[
                inEditMode
                    ? 'hover:bg-surface-gray-2'
                    : 'cursor-pointer hover:bg-surface-gray-2 active:bg-surface-gray-3',
                { 'opacity-50 cursor-not-allowed': disabled },
            ]"
        >
            <label class="flex items-center gap-2 flex-1">
                <Checkbox
                    :modelValue="selected.includes(option)"
                    :disabled="disabled"
                    size="sm"
                    @update:modelValue="toggle(option, $event)"
                />
                <span class="text-base text-ink-gray-8 select-none">{{ option }}</span>
            </label>
            <Button
                v-if="inEditMode"
                variant="ghost"
                icon="x"
                size="sm"
                class="!size-5 pointer-events-auto"
                @click.stop="removeOption(option)"
            />
        </div>
        <span v-if="!options?.length" class="text-sm text-ink-gray-4 italic">
            No options defined
        </span>
    </div>
</template>
