<script setup lang="ts">
import { computed } from "vue";

type Props = {
    teamName: string;
    logoUrl: string | null;
    classNames?: string;
};

const props = withDefaults(defineProps<Props>(), {
    classNames: "size-5 rounded-full object-cover",
});

const AVATAR_BASE = "/assets/forms_pro/avatars/avatar-";

/** Derives a stable 1–50 index from the team name (length + first/last char) so the same name always maps to the same avatar when no logoUrl is set. */
function avatarIndex(name: string): number {
    const n = name.length;
    if (n === 0) return 1;
    const h = n + name.charCodeAt(0) + (n > 1 ? name.charCodeAt(n - 1) : 0);
    return (((h % 50) + 50) % 50) + 1;
}

const avatarSrc = computed(() =>
    props.logoUrl ? props.logoUrl : `${AVATAR_BASE}${avatarIndex(props.teamName)}.jpg`
);
</script>

<template>
    <img :src="avatarSrc" :alt="teamName" :class="classNames" />
</template>
