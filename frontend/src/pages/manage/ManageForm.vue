<script setup lang="ts">
import BaseLayout from "@/layouts/BaseLayout.vue";
import RouteError from "@/components/RouteError.vue";
import { watch } from "vue";
import { useManageForm } from "@/stores/form/manageForm";
import { useRouteData } from "@/composables/useRouteData";
import { useRoute } from "vue-router";
import { useManageFormSidebarItems } from "./sidebarItems";

const manageFormStore = useManageForm();
const route = useRoute();
const sidebarItems = useManageFormSidebarItems();
const { status, error } = useRouteData();

watch(
    () => route.params.id,
    (id) => {
        manageFormStore.initialize(id as string);
    },
    { immediate: true }
);
</script>

<template>
    <RouteError
        v-if="status === 'error'"
        :exc-type="error?.excType"
        :http-status="error?.httpStatus"
        :messages="error?.messages"
    />
    <BaseLayout v-else :sidebar-sections="sidebarItems">
        <router-view />
    </BaseLayout>
</template>
