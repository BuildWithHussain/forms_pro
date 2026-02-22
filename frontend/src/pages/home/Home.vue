<script setup lang="ts">
import BaseLayout from "@/layouts/BaseLayout.vue";
import { useUser } from "@/stores/user";
import { useSidebarItems } from "./sidebarItems";
const userStore = useUser();
userStore.initialize();

const sidebarItems = useSidebarItems();
</script>
<template>
    <BaseLayout :sidebar-sections="sidebarItems">
        <router-view />
    </BaseLayout>
</template>
