<script setup lang="ts">
import { Asterisk } from "lucide-vue-next";

defineProps<{
    field: {
        label?: string;
        reqd?: boolean;
    };
    inEditMode: boolean;
}>();

const emit = defineEmits<{
    "update:label": [value: string];
}>();
</script>

<template>
    <div class="flex gap-2 items-start">
        <input
            v-if="inEditMode"
            placeholder="Label"
            type="text"
            :value="field.label"
            @input="emit('update:label', ($event.target as HTMLInputElement).value)"
            class="bg-transparent border-none outline-none text-base focus:ring-0 w-fit px-0 py-1"
        />
        <label class="text-base" v-else>{{ field.label }}</label>
        <Asterisk v-if="field.reqd" class="w-4 h-4 text-red-400" />
    </div>
</template>
