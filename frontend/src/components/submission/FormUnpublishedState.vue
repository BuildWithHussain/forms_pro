<script setup lang="ts">
import { Unplug } from "lucide-vue-next";
</script>

<template>
    <div class="flex flex-col items-center justify-center text-ink-gray-8">
        <Unplug class="w-10 h-10" />
        <h1 class="text-2xl font-bold">Form is un-published!</h1>
        <p class="text-base text-ink-gray-6">
            The form has been unpublished by its creator, so responses are no longer being
            collected.
        </p>
    </div>
</template>
