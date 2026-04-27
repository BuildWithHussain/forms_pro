<script setup lang="ts">
import { Dialog } from "frappe-ui";
import { dialogState } from "@/utils/dialog";
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
            <p
                v-if="dialogState.html"
                class="text-p-base text-gray-700"
                v-html="dialogState.message"
            ></p>
            <p v-else class="text-p-base text-gray-700">
                {{ dialogState.message }}
            </p>
        </template>
    </Dialog>
</template>
