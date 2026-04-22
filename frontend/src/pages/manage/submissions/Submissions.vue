<script setup lang="ts">
import { useManageForm } from "@/stores/form/manageForm";
import { ListChecks } from "@lucide/vue";
import { Breadcrumbs } from "frappe-ui";
import { computed } from "vue";
import SubmissionList from "@/components/form/submissions/SubmissionList.vue";

const manageFormStore = useManageForm();
const breadcrumbItems = computed(() => [
    { label: "Manage Form", to: `/manage/${manageFormStore.currentFormId}/overview` },
    { label: "Submissions" },
]);
</script>

<template>
    <div class="flex flex-col gap-4 w-full">
        <Breadcrumbs :items="breadcrumbItems" />
        <div class="flex flex-col gap-4">
            <div class="flex gap-3 items-center text-ink-gray-8">
                <ListChecks class="w-6 h-6" />
                <h2 class="text-2xl font-bold">Submissions</h2>
            </div>
            <p class="text-ink-gray-5 text-sm">
                Form submissions for
                <span class="text-sm p-1 bg-surface-gray-1 font-mono">{{
                    manageFormStore.formData?.title
                }}</span>
                will appear here.
            </p>
            <SubmissionList />
        </div>
    </div>
</template>
