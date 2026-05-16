<script setup lang="ts">
import { computed } from "vue";
import { Rating as FrappeRating } from "frappe-ui";

// Frappe stores Rating as a 0..1 fraction (see `_fix_rating_value` in
// frappe.model.document — values are clamped to [0, 1]). frappe-ui's Rating
// component, however, works in raw 1..N integers. Passing a 0..1 float in or
// emitting a 1..N int out silently corrupts the value. This wrapper bridges
// the two representations so the underlying fraction round-trips intact.

const MAX_STARS = 5;

defineProps<{
    readonly?: boolean;
    disabled?: boolean;
}>();

const modelValue = defineModel<number | null>();

const starValue = computed(() => Math.round((Number(modelValue.value) || 0) * MAX_STARS));

const onUpdate = (stars: number) => {
    modelValue.value = stars / MAX_STARS;
};
</script>

<template>
    <FrappeRating
        :modelValue="starValue"
        :rating_from="MAX_STARS"
        :readonly="readonly || disabled"
        @update:modelValue="onUpdate"
    />
</template>
