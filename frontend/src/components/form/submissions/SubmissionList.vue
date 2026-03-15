<script setup lang="ts">
import { useManageForm } from "@/stores/form/manageForm";
import { ListView, Badge, createResource } from "frappe-ui";
import { formatDateTime } from "@/utils/date";
import Avatar from "@/components/ui/Avatar.vue";
import { computed, onMounted, ref } from "vue";
import { toast } from "vue-sonner";

const manageFormStore = useManageForm();
const isLoading = ref(false);

const allSubmissionsResource = createResource({
    url: "forms_pro.api.submission.get_all_submissions",
    makeParams() {
        return {
            form_id: manageFormStore.currentFormId,
        };
    },
    onSuccess() {
        isLoading.value = false;
    },
    onError(error: Error) {
        toast.error("Failed to fetch submissions", {
            description: error.message,
        });
    },
});
const allSubmissions = computed(() => allSubmissionsResource.data ?? []);

onMounted(() => {
    isLoading.value = true;
    allSubmissionsResource.fetch();
});

const columns = computed(() => [
    {
        label: "ID",
        key: "name",
        width: 1,
    },
    {
        label: "Status",
        key: "submission_status",
        width: 1,
    },
    {
        label: "Submitted On",
        key: "creation",
        width: 2,
    },
    {
        label: "Last Modified",
        key: "modified",
        width: 2,
    },
    {
        label: "Submitted By",
        key: "owner",
        width: 1,
    },
]);
</script>
<template>
    <ListView
        :columns="columns"
        :rows="allSubmissions"
        :options="{
            selectable: false,
            showTooltip: false,
            emptyState: {
                title: 'No Submissions Yet',
                description: 'Submissions for this form will appear here.',
            },
        }"
        row-key="name"
    >
        <!-- @vue-expect-error -->
        <template #cell="{ item, row, column }">
            <div v-if="column.key === 'owner'" class="flex items-center gap-2">
                <Avatar v-if="row.owner !== 'Guest'" :userId="row.owner" />
                <span class="text-sm text-ink-gray-8">{{ row.owner }}</span>
            </div>
            <span v-else-if="column.key === 'name'" class="text-xs text-ink-gray-6 font-mono">
                {{ row.name }}
            </span>
            <Badge
                v-else-if="column.key === 'submission_status'"
                :label="row.submission_status"
                :variant="row.submission_status === 'Submitted' ? 'subtle' : 'outline'"
            />
            <span v-else-if="column.key === 'creation'" class="text-sm text-ink-gray-6">
                {{ formatDateTime(row.creation) }}
            </span>
            <span v-else-if="column.key === 'modified'" class="text-sm text-ink-gray-6">
                {{ formatDateTime(row.modified) }}
            </span>
            <span v-else class="text-sm">{{ item }}</span>
        </template>
    </ListView>
</template>
