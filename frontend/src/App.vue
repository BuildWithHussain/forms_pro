<script setup lang="ts">
import "vue-sonner/style.css";
import { Toaster } from "vue-sonner";
import GlobalDialog from "@/components/ui/GlobalDialog.vue";
import { useUser } from "@/stores/user";

const userStore = useUser();
userStore.initialize();
</script>

<template>
    <div>
        <router-view />
    </div>
    <Toaster theme="system" />
    <GlobalDialog />
</template>
