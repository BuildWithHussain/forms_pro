<script setup lang="ts">
import { Fieldtype } from "@/types/FormsPro/form_field.types";
import { computed } from "vue";

const props = defineProps<{
    field: {
        label: string;
        fieldtype: Fieldtype;
    };
    inEditMode: boolean;
}>();

const emit = defineEmits<{
    "update:label": [value: string];
}>();

const headingClasses: Record<HeadingFieldtype, string> = {
    [Fieldtype.HEADING_1]: "text-xl font-bold",
    [Fieldtype.HEADING_2]: "text-lg font-semibold",
    [Fieldtype.HEADING_3]: "text-base font-semibold",
};

type HeadingFieldtype = Fieldtype.HEADING_1 | Fieldtype.HEADING_2 | Fieldtype.HEADING_3;
type HeadingTag = "h2" | "h3" | "h4";

const headingTypeToTag: Record<HeadingFieldtype, HeadingTag> = {
    [Fieldtype.HEADING_1]: "h2",
    [Fieldtype.HEADING_2]: "h3",
    [Fieldtype.HEADING_3]: "h4",
};

const headingTag = computed<HeadingTag>(
    () => headingTypeToTag[props.field.fieldtype as HeadingFieldtype] ?? "h2"
);

const headingClass = computed(
    () => headingClasses[props.field.fieldtype as HeadingFieldtype] ?? ""
);
</script>

<template>
    <div v-if="inEditMode">
        <input
            type="text"
            :value="field.label"
            @input="emit('update:label', ($event.target as HTMLInputElement).value)"
            :class="[
                headingClass,
                'bg-transparent border-none outline-none text-base focus:ring-0 w-full px-0 py-1',
            ]"
            placeholder="Heading Text"
        />
    </div>
    <component v-else :is="headingTag" :class="headingClass">
        {{ field.label }}
    </component>
</template>
