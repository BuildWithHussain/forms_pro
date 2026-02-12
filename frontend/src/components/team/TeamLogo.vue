<script setup lang="ts">
import { computed } from "vue";

type props = {
    teamName: string;
    logoUrl: string | null;
};

const props = defineProps<props>();

function hashToAvatarIndex(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash = hash | 0;
    }
    return (Math.abs(hash) % 50) + 1;
}

const avatarSrc = computed(() => {
    if (props.logoUrl) {
        return props.logoUrl;
    }
    const index = hashToAvatarIndex(props.teamName);
    return `/assets/forms_pro/avatars/avatar-${index}.jpg`;
});
</script>

<template>
    <img :src="avatarSrc" :alt="teamName" class="size-5 rounded-full object-cover" />
</template>
