<script setup lang="ts">
import { useManageForm } from "@/stores/form/manageForm";

const manageFormStore = useManageForm();
</script>
<template>
    <p class="prose-sm text-ink-gray-5" v-if="!manageFormStore.formData?.description">
        No description added for this form.
    </p>
    <div class="prose-sm mb-6" v-html="manageFormStore.formData?.description"></div>
</template>
