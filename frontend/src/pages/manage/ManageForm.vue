<script setup lang="ts">
import BaseLayout from "@/layouts/BaseLayout.vue";
import { watch } from "vue";
import { useManageForm } from "@/stores/form/manageForm";
import { useRoute } from "vue-router";
import { useManageFormSidebarItems } from "./sidebarItems";

const manageFormStore = useManageForm();
const route = useRoute();
const sidebarItems = useManageFormSidebarItems();

watch(
    () => route.params.id,
    (id) => {
        manageFormStore.initialize(id as string);
    },
    { immediate: true }
);
</script>

<template>
    <BaseLayout :sidebar-sections="sidebarItems">
        <router-view />
    </BaseLayout>
</template>
