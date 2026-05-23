<script setup lang="ts">
import "vue-sonner/style.css";
import { Toaster } from "vue-sonner";
import { LoadingIndicator } from "frappe-ui";
import GlobalDialog from "@/components/ui/GlobalDialog.vue";
import { useRouteData } from "@/stores/routeData";
import { useUser } from "@/stores/user";

const userStore = useUser();
userStore.initialize();

const routeData = useRouteData();
</script>

<template>
    <div>
        <router-view />
    </div>
    <LoadingIndicator v-if="routeData.isNavigating" class="fixed top-4 right-4 z-50" />
    <Toaster theme="system" />
    <GlobalDialog />
</template>
