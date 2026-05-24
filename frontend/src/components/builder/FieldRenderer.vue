<script setup lang="ts">
import { computed } from "vue";
import RenderField from "../RenderField.vue";
import FieldLabel from "./FieldLabel.vue";
import Heading from "@/components/fields/Heading.vue";
import Table from "@/components/fields/Table.vue";
import { useFieldOptions } from "@/utils/selectOptions";
import { getFieldTypeDef, Fieldtype } from "@/config/fieldTypes";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
    inEditMode: {
        type: Boolean,
        required: true,
    },
    disabled: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const emit = defineEmits(["update:field"]);
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const modelValue = defineModel<any>();

const fieldData = computed({
    get() {
        return props.field;
    },
    set(value) {
        emit("update:field", value);
    },
});

const layout = computed(
    () => getFieldTypeDef(fieldData.value.fieldtype as Fieldtype)?.layout ?? "default"
);

const builderExtrasComponent = computed(
    () => getFieldTypeDef(fieldData.value.fieldtype as Fieldtype)?.builderExtras ?? null
);

const { options: selectOptions } = useFieldOptions(fieldData);
</script>

<template>
    <div class="w-full flex flex-col gap-2">
        <!-- inline: Switch / Checkbox — input precedes label -->
        <div v-if="layout === 'inline'" class="w-full flex gap-2 my-2">
            <RenderField
                v-model="modelValue"
                :field="fieldData"
                :class="{ 'pointer-events-none mt-1': inEditMode }"
                :disabled="disabled"
            />
            <div class="flex flex-col gap-1 w-full">
                <FieldLabel
                    :field="fieldData"
                    :in-edit-mode="inEditMode"
                    @update:label="fieldData.label = $event"
                />
                <small class="text-gray-500">{{ fieldData.description }}</small>
            </div>
        </div>

        <!-- description-first: label → description → input (Text Editor, Multiselect) -->
        <div v-else-if="layout === 'description-first'" class="flex flex-col gap-1">
            <FieldLabel
                :field="fieldData"
                :in-edit-mode="inEditMode"
                @update:label="fieldData.label = $event"
            />
            <small class="text-gray-500">{{ fieldData.description }}</small>
            <RenderField
                v-model="modelValue"
                :field="fieldData"
                :in-edit-mode="inEditMode"
                :class="{ 'pointer-events-none': inEditMode }"
                :disabled="disabled"
            />
        </div>

        <!-- heading: renders field label as h1/h2/h3; no input -->
        <div v-else-if="layout === 'heading'" class="w-full py-1">
            <Heading
                :field="fieldData"
                :in-edit-mode="inEditMode"
                @update:label="fieldData.label = $event"
            />
        </div>

        <!-- custom: Attach and Table each need their own binding/widget -->
        <div v-else-if="layout === 'custom' && fieldData.fieldtype === 'Attach'">
            <FieldLabel
                :field="fieldData"
                :in-edit-mode="inEditMode"
                @update:label="fieldData.label = $event"
            />
            <RenderField
                v-model="modelValue"
                :field="fieldData"
                :class="{ 'pointer-events-none': inEditMode }"
                :disabled="disabled"
            />
            <small class="text-gray-500">{{ fieldData.description }}</small>
        </div>

        <div v-else-if="layout === 'custom'" class="w-full space-y-4">
            <FieldLabel
                :field="fieldData"
                :in-edit-mode="inEditMode"
                @update:label="fieldData.label = $event"
            />
            <small class="text-gray-500">{{ fieldData.description }}</small>
            <Table v-model="modelValue" :in-edit-mode="inEditMode" :doctype="fieldData.options" />
        </div>

        <!-- default: label → input → description -->
        <div v-else class="w-full flex flex-col gap-2">
            <FieldLabel
                :field="fieldData"
                :in-edit-mode="inEditMode"
                @update:label="fieldData.label = $event"
            />
            <RenderField
                v-model="modelValue"
                :field="fieldData"
                :class="{ 'pointer-events-none': inEditMode }"
                :disabled="disabled"
                :options="selectOptions"
            />
            <small class="text-gray-500">{{ fieldData.description }}</small>
        </div>

        <component
            v-if="inEditMode && builderExtrasComponent"
            :is="builderExtrasComponent"
            :field="fieldData"
            @update:field="fieldData = $event"
        />
    </div>
</template>
