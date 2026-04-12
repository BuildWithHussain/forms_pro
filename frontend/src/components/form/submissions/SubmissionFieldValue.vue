<script setup lang="ts">
import { Checkbox, Switch, Rating, TextEditor } from "frappe-ui";
import { Fieldtype } from "@/types/formfield";
import { getFieldTypeDef } from "@/config/fieldTypes";
import { formatDate, formatDateTime, formatTime } from "@/utils/date";
import { computed } from "vue";

const props = defineProps<{
    fieldname: string;
    label: string;
    description?: string;
    fieldtype: Fieldtype;
    value: any;
}>();

const formattedDateValue = computed(() => {
    if (!props.value) return "";
    switch (props.fieldtype) {
        case Fieldtype.DATE:
            return formatDate(props.value);
        case Fieldtype.DATE_TIME:
            return formatDateTime(props.value);
        case Fieldtype.TIME_PICKER:
            return formatTime(props.value);
        case Fieldtype.DATE_RANGE:
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

const typeDef = computed(() => getFieldTypeDef(props.fieldtype));
const isDateField = computed(() => typeDef.value?.isDate ?? false);

// Only allow safe attachment URLs (relative Frappe paths or http/https).
// Rejects javascript: and other unsafe schemes.
const safeAttachUrl = computed<string | null>(() => {
    if (!props.value) return null;
    const url = String(props.value);
    if (url.startsWith("/")) return url;
    try {
        const { protocol } = new URL(url);
        if (protocol === "https:" || protocol === "http:") return url;
    } catch {
        // unparseable — not a valid URL
    }
    return null;
});

const classNames = computed<string>(() =>
    typeDef.value?.isBoolean
        ? "flex gap-1 flex-row-reverse items-start justify-end"
        : "flex flex-col gap-1"
);
</script>

<template>
    <div :class="classNames">
        <div>
            <span class="text-sm text-ink-gray-5">{{ label }}</span>
            <p v-if="description" class="text-xs text-ink-gray-4">{{ description }}</p>
        </div>

        <Checkbox
            v-if="fieldtype === Fieldtype.CHECKBOX"
            class="mt-1"
            :modelValue="Boolean(value)"
            disabled
        />

        <Switch v-else-if="fieldtype === Fieldtype.SWITCH" :modelValue="Boolean(value)" disabled />

        <TextEditor
            v-else-if="fieldtype === Fieldtype.TEXT_EDITOR"
            :content="value"
            :editable="false"
            :bubbleMenu="false"
            :fixedMenu="false"
            editorClass="prose-sm !border-none !p-0 !shadow-none"
        />

        <Rating v-else-if="fieldtype === Fieldtype.RATING" :modelValue="value" readonly />

        <a
            v-else-if="fieldtype === Fieldtype.ATTACH && safeAttachUrl"
            :href="safeAttachUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="text-sm text-blue-600 hover:text-blue-700 underline truncate"
        >
            {{ value }}
        </a>
        <span v-else-if="fieldtype === Fieldtype.ATTACH && value" class="text-sm text-ink-gray-5">
            {{ value }}
        </span>

        <span
            v-else-if="fieldtype === Fieldtype.TEXTAREA"
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
