<script setup lang="ts">
import { createResource } from "frappe-ui";
import { useManageForm } from "@/stores/form/manageForm";
import { computed, watch } from "vue";
import { toast } from "vue-sonner";
import { formatDateTime } from "@/utils/date";
import SubmissionFieldValue from "@/components/form/submissions/SubmissionFieldValue.vue";

const props = defineProps<{
    submissionId: string;
    doctype: string;
}>();

const manageFormStore = useManageForm();

const submissionResource = createResource({
    url: "forms_pro.api.submission.get_submission_response",
    makeParams() {
        return {
            submission_id: props.submissionId,
            doctype: props.doctype,
        };
    },
    onError(error: Error) {
        toast.error("Failed to fetch submission details", {
            description: error.message,
        });
    },
});

const submissionData = computed(() => submissionResource.data ?? null);

watch(
    () => props.submissionId,
    (newId) => {
        if (newId) {
            submissionResource.fetch();
        }
    },
    { immediate: true }
);

const gridItems = computed(() => [
    {
        label: "Submission ID",
        key: "name",
        value: submissionData.value?.name,
        class: "font-mono",
    },
    {
        label: "Submitted On",
        key: "creation",
        value: formatDateTime(submissionData.value?.creation),
    },
    {
        label: "Last Modified",
        key: "modified",
        value: formatDateTime(submissionData.value?.modified),
    },
    {
        label: "Submitted By",
        key: "owner",
        value: submissionData.value?.owner,
    },
]);
</script>

<template>
    <div v-if="submissionResource.loading" class="text-sm text-ink-gray-5">Loading...</div>
    <div v-else-if="submissionData" class="flex flex-col gap-4">
        <div class="p-2 flex flex-col gap-4">
            <div class="grid grid-cols-3 gap-4">
                <template v-for="item in gridItems" :key="item.key">
                    <span class="text-sm text-ink-gray-5">{{ item.label }}</span>
                    <span class="text-sm text-ink-gray-7 col-span-2" :class="item.class">{{
                        item.value
                    }}</span>
                </template>
            </div>
            <hr />
            <div class="flex flex-col gap-6 my-4">
                <SubmissionFieldValue
                    v-for="field in manageFormStore.formFields"
                    :key="field.name"
                    :fieldname="field.fieldname"
                    :label="field.label"
                    :description="field.description"
                    :fieldtype="field.fieldtype"
                    :value="submissionData[field.fieldname]"
                />
            </div>
        </div>
    </div>
</template>
