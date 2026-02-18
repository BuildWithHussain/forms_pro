<script setup lang="ts">
import { computed } from "vue";
import { Asterisk } from "lucide-vue-next";
import RenderField from "../RenderField.vue";
import Table from "@/components/fields/Table.vue";
import { useFieldOptions } from "@/utils/selectOptions";

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

// Add v-model support
const modelValue = defineModel();

// Create a computed property for two-way binding
const fieldData = computed({
    get() {
        return props.field;
    },
    set(value) {
        emit("update:field", value);
    },
});

const getClasses = computed(() => {
    switch (fieldData.value.fieldtype) {
        case "Text Editor":
            return "w-fit";
        case "Switch":
            return "w-full flex gap-4 my-2";
        case "Checkbox":
            return "w-full flex gap-2";
        default:
            return "w-full flex flex-col gap-2";
    }
});

const { options: selectOptions } = useFieldOptions(fieldData);
</script>
<template>
    <div :class="getClasses" v-if="fieldData.fieldtype == 'Switch'">
        <RenderField
            v-model="modelValue"
            :field="fieldData"
            :class="{ 'pointer-events-none': inEditMode }"
            :disabled="disabled"
        />
        <div class="flex flex-col gap-1">
            <div class="flex gap-2 items-start">
                <input
                    v-if="inEditMode"
                    placeholder="Label"
                    type="text"
                    v-model="fieldData.label"
                    class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
                />
                <label class="text-base" v-else>{{ fieldData.label }}</label>
                <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
            </div>
            <small class="text-gray-500">
                {{ fieldData.description }}
            </small>
        </div>
    </div>
    <div :class="getClasses" v-else-if="fieldData.fieldtype == 'Checkbox'">
        <RenderField
            v-model="modelValue"
            :field="fieldData"
            :class="{ 'pointer-events-none mt-1': inEditMode }"
            :disabled="disabled"
        />
        <div class="flex flex-col gap-1 w-full">
            <div class="flex gap-2 items-start">
                <input
                    v-if="inEditMode"
                    :id="fieldData.name + '_label'"
                    placeholder="Label"
                    type="text"
                    v-model="fieldData.label"
                    class="bg-transparent border-none outline-none text-base focus:ring-0 px-0 py-1 !w-full"
                />
                <label class="text-base" v-else>{{ fieldData.label }}</label>
                <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
            </div>
            <small v-if="fieldData.description" class="text-gray-500">
                {{ fieldData.description }}
            </small>
        </div>
    </div>
    <div v-else-if="fieldData.fieldtype == 'Text Editor'">
        <div class="flex flex-col gap-1">
            <div class="flex gap-2 items-start">
                <input
                    v-if="inEditMode"
                    placeholder="Label"
                    type="text"
                    v-model="fieldData.label"
                    class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
                />
                <label class="text-base" v-else>{{ fieldData.label }}</label>
                <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
            </div>
            <small class="text-gray-500">
                {{ fieldData.description }}
            </small>
            <RenderField
                :model-value="modelValue"
                :field="fieldData"
                @change="(value: any) => (modelValue = value)"
                :class="{ 'pointer-events-none': inEditMode }"
                :disabled="disabled"
            />
        </div>
    </div>
    <div v-else-if="fieldData.fieldtype == 'Attach'">
        <div class="flex gap-2 items-start">
            <input
                v-if="inEditMode"
                placeholder="Label"
                type="text"
                v-model="fieldData.label"
                class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
            />
            <label class="text-base" v-else>{{ fieldData.label }}</label>
            <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
        </div>
        <RenderField
            :value="modelValue"
            @update:value="(value: string) => (modelValue = value)"
            :field="fieldData"
            :class="{ 'pointer-events-none': inEditMode }"
            :disabled="disabled"
        />
        <small class="text-gray-500">
            {{ fieldData.description }}
        </small>
    </div>
    <div v-else-if="fieldData.fieldtype == 'Table'" class="w-full space-y-4">
        <div class="flex gap-2 items-start">
            <input
                v-if="inEditMode"
                placeholder="Label"
                type="text"
                v-model="fieldData.label"
                class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
            />
            <label class="text-base" v-else>{{ fieldData.label }}</label>
            <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
        </div>
        <small class="text-gray-500">
            {{ fieldData.description }}
        </small>
        <Table
            v-model="modelValue as undefined"
            :in-edit-mode="inEditMode"
            :doctype="fieldData.options"
        />
    </div>
    <div v-else :class="getClasses">
        <div class="flex gap-2 items-start">
            <input
                v-if="inEditMode"
                placeholder="Label"
                type="text"
                v-model="fieldData.label"
                class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
            />
            <label class="text-base" v-else>{{ fieldData.label }}</label>
            <Asterisk v-if="fieldData.reqd" class="w-4 h-4 text-red-400" />
        </div>
        <RenderField
            v-model="modelValue"
            :field="fieldData"
            :class="{ 'pointer-events-none': inEditMode }"
            :disabled="disabled"
            :options="selectOptions"
        />
        <small class="text-gray-500">
            {{ fieldData.description }}
        </small>
    </div>
</template>
