<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { Asterisk } from "lucide-vue-next";
import RenderField from "../RenderField.vue";
import { createResource } from "frappe-ui";

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

type SelectOption = {
    label: string;
    value: string;
};

// Reactive ref to store options
const selectOptions = ref<string[] | SelectOption[] | null>(null);

const getOptions = async () => {
    if (!fieldData.value.options) {
        return "";
    }

    if (fieldData.value.fieldtype === "Select") {
        return fieldData.value.options.split("\n");
    }

    if (fieldData.value.fieldtype === "Link") {
        const _options = createResource({
            url: "forms_pro.api.form.get_link_field_options",
            makeParams: () => {
                return {
                    doctype: fieldData.value.options,
                    filters: {},
                    page_length: 999,
                };
            },
        });
        await _options.fetch();
        return _options.data;
    }

    return fieldData.value.options;
};

// Load options when component mounts or field data changes
const loadOptions = async () => {
    selectOptions.value = await getOptions();
};

// Watch for changes to field type or options
watch(
    () => [fieldData.value.fieldtype, fieldData.value.options],
    () => {
        loadOptions();
    },
    { immediate: true }
);

// Also load on mount
onMounted(() => {
    loadOptions();
});
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
