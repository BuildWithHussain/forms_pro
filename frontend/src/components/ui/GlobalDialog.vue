<script setup lang="ts">
import { Dialog, Button } from "frappe-ui";
import { dialogState, dialog } from "@/utils/dialog";
</script>

<template>
    <Dialog
        v-model="dialogState.open"
        :options="{
            title: dialogState.title,
            actions: dialogState.actions,
        }"
    >
        <template #body-content>
            <p class="text-p-base text-gray-700">{{ dialogState.message }}</p>
        </template>
    </Dialog>
</template>
