<script setup lang="ts">
type props = {
    label: string;
    imgUrl?: string;
};

const props = defineProps<props>();
</script>
<template>
    <div class="flex items-center gap-2 shrink-0">
        <img :src="imgUrl" alt="Team Logo" class="size-5 rounded-sm" />
        <span class="text-base font-medium text-ink-gray-7 whitespace-nowrap">
            {{ label }}
        </span>
    </div>
</template>
