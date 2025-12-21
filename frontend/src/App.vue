<script setup lang="ts">
import "vue-sonner/style.css";
import { Toaster } from "vue-sonner";
import { useUser } from "@/stores/user";

const userStore = useUser();
userStore.initialize();
</script>

<template>
    <div>
        <router-view />
    </div>
    <Toaster theme="system" />
</template>
