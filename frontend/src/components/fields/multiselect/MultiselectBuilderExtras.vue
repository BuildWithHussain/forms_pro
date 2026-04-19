<script setup lang="ts">
import { ref, nextTick } from "vue";
import { FormControl, ErrorMessage } from "frappe-ui";

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

const errorMessage = ref("");

function dismissIfEmpty() {
    if (!newOptionValue.value.trim()) {
        isAddingOption.value = false;
        errorMessage.value = "";
    }
}

function addOption() {
    errorMessage.value = "";

    const value = newOptionValue.value.trim();
    if (!value) return;

    const items = new Set((props.field.options ?? "").split("\n").filter(Boolean));

    if (items.has(value)) {
        errorMessage.value = "This option already exists in the list";
        return;
    }

    items.add(value);
    emit("update:field", {
        ...props.field,
        options: [...items].join("\n"),
    });
    newOptionValue.value = "";
    isAddingOption.value = false;
}
</script>

<template>
    <ErrorMessage class="text-xs" :message="errorMessage" />
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
        @blur="dismissIfEmpty"
    />
    <Button
        v-else
        class="w-fit"
        variant="ghost"
        label="Add Option"
        icon-left="plus"
        @click="startAddingOption"
    />
</template>
