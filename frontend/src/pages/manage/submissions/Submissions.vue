<script setup lang="ts">
import { useManageForm } from "@/stores/form/manageForm";
import { ListChecks } from "lucide-vue-next";
import { Breadcrumbs, LoadingText } from "frappe-ui";
import { computed } from "vue";

const manageFormStore = useManageForm();

const breadcrumbItems = computed(() => [
    { label: "Manage Form", to: `/manage/${manageFormStore.currentFormId}/overview` },
    { label: "Submissions" },
]);
</script>

<template>
    <div class="flex flex-col gap-4 w-full overflow-y-auto">
        <Breadcrumbs :items="breadcrumbItems" />
        <div v-if="manageFormStore.formResource.value?.loading">
            <LoadingText />
        </div>
        <div v-else-if="manageFormStore.formData" class="flex flex-col gap-4">
            <div class="flex gap-3 items-center text-ink-gray-8">
                <ListChecks class="w-6 h-6" />
                <h2 class="text-2xl font-bold">Submissions</h2>
            </div>
            <p class="text-ink-gray-5 text-sm">
                Form submissions for {{ manageFormStore.formData?.title }} will appear here.
            </p>
        </div>
    </div>
</template>
