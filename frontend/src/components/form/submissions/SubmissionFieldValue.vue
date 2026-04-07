<script setup lang="ts">
import { Checkbox, Switch, Rating, TextEditor } from "frappe-ui";
import { FormFieldTypes } from "@/types/formfield";
import { formatDate, formatDateTime, formatTime } from "@/utils/date";
import { computed } from "vue";

const props = defineProps<{
    fieldname: string;
    label: string;
    description?: string;
    fieldtype: FormFieldTypes;
    value: any;
}>();

const formattedDateValue = computed(() => {
    if (!props.value) return "";
    switch (props.fieldtype) {
        case FormFieldTypes.Date:
            return formatDate(props.value);
        case FormFieldTypes.DateTime:
            return formatDateTime(props.value);
        case FormFieldTypes.TimePicker:
            return formatTime(props.value);
        case FormFieldTypes.DateRange:
            try {
                const dates = JSON.parse(props.value);
                if (Array.isArray(dates) && dates.length === 2) {
                    return `${formatDate(dates[0])} – ${formatDate(dates[1])}`;
                }
            } catch {
                /* value might already be a readable string */
            }
            return String(props.value);
        default:
            return String(props.value);
    }
});

const isDateField = computed(() =>
    [
        FormFieldTypes.Date,
        FormFieldTypes.DateTime,
        FormFieldTypes.DateRange,
        FormFieldTypes.TimePicker,
    ].includes(props.fieldtype)
);

const classNames = computed<string>(() => {
    if ([FormFieldTypes.Switch, FormFieldTypes.Checkbox].includes(props.fieldtype)) {
        return "flex gap-1 flex-row-reverse items-start justify-end";
    }
    return "flex flex-col gap-1";
});
</script>

<template>
    <div :class="classNames">
        <div>
            <span class="text-sm text-ink-gray-5">{{ label }}</span>
            <p v-if="description" class="text-xs text-ink-gray-4">{{ description }}</p>
        </div>

        <Checkbox
            v-if="fieldtype === FormFieldTypes.Checkbox"
            class="mt-1"
            :modelValue="Boolean(value)"
            disabled
        />

        <Switch
            v-else-if="fieldtype === FormFieldTypes.Switch"
            :modelValue="Boolean(value)"
            disabled
        />

        <TextEditor
            v-else-if="fieldtype === FormFieldTypes.TextEditor"
            :content="value"
            :editable="false"
            :bubbleMenu="false"
            :fixedMenu="false"
            editorClass="prose-sm !border-none !p-0 !shadow-none"
        />

        <Rating v-else-if="fieldtype === FormFieldTypes.Rating" :modelValue="value" readonly />

        <a
            v-else-if="fieldtype === FormFieldTypes.Attach && value"
            :href="value"
            target="_blank"
            class="text-sm text-blue-600 hover:text-blue-700 underline truncate"
        >
            {{ value }}
        </a>

        <span
            v-else-if="fieldtype === FormFieldTypes.Textarea"
            class="text-sm text-ink-gray-7 whitespace-pre-wrap"
        >
            {{ value ?? "–" }}
        </span>

        <span v-else-if="isDateField" class="text-sm text-ink-gray-7">
            {{ formattedDateValue }}
        </span>

        <span v-else class="text-sm text-ink-gray-7">
            {{ value ?? "–" }}
        </span>
    </div>
</template>
