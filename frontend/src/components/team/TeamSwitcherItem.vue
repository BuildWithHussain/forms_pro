<script setup lang="ts">
import TeamLogo from "./TeamLogo.vue";

type props = {
    label: string;
    logoUrl: string | null;
};

const props = defineProps<props>();
</script>
<template>
    <div class="flex items-center gap-2 shrink-0">
        <TeamLogo :team-name="label" :logo-url="logoUrl" />
        <span class="text-base font-medium text-ink-gray-7 whitespace-nowrap">
            {{ label }}
        </span>
    </div>
</template>
