<script setup lang="ts">
import { ref, nextTick } from "vue";
import { FormControl } from "frappe-ui"; // Button is globally registered in main.ts

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const props = defineProps<{ field: Record<string, any> }>();
const emit = defineEmits<{ (e: "update:field", value: typeof props.field): void }>();

const isAddingOption = ref(false);
const newOptionValue = ref("");
const newOptionInput = ref<InstanceType<typeof FormControl> | null>(null);

async function startAddingOption() {
    isAddingOption.value = true;
    await nextTick();
    newOptionInput.value?.$el?.querySelector("input")?.focus();
}

function addOption() {
    const value = newOptionValue.value.trim();
    if (!value) return;

    const current = props.field.options ?? "";
    emit("update:field", {
        ...props.field,
        options: current ? `${current}\n${value}` : value,
    });
    newOptionValue.value = "";
}
</script>

<template>
    <FormControl
        v-if="isAddingOption"
        ref="newOptionInput"
        v-model="newOptionValue"
        type="text"
        variant="outline"
        size="sm"
        placeholder="Type option and press Enter"
        @keydown.enter.prevent="addOption"
        @keydown.escape="isAddingOption = false"
    />
    <Button
        v-else
        variant="ghost"
        label="Add Option"
        icon-left="plus"
        @click="startAddingOption"
    />
</template>
