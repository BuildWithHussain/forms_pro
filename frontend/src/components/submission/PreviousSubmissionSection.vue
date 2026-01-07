<script setup lang="ts">
import { useSubmissionForm } from "@/stores/submissionForm";
import { Button } from "frappe-ui";
import { formatDateTime } from "@/utils/date";
import { Badge } from "frappe-ui";

const submissionFormStore = useSubmissionForm();
</script>
<template>
    <div
        v-if="submissionFormStore.userSubmissions"
        class="max-w-screen-md mx-auto mt-16 shadow-[0_0_10px_0_rgba(0,0,0,0.1)] border bg-surface-white rounded-lg p-6 space-y-4"
    >
        <h2 class="text-2xl font-bold">Previous Submissions</h2>
        <p class="text-base text-ink-gray-6">Here are your previous submissions for this form.</p>
        <div
            v-for="(submission, index) in submissionFormStore.userSubmissions"
            :key="submission.name"
            class="flex justify-between w-full items-center border p-4 rounded-lg"
        >
            <div class="text-lg font-medium space-y-2 flex flex-col">
                <h4>Submission #{{ index + 1 }}</h4>

                <div class="flex gap-2 items-center">
                    <Badge
                        v-if="submission.fp_submission_status"
                        :label="submission.fp_submission_status"
                        :variant="
                            submission.fp_submission_status === 'Submitted' ? 'subtle' : 'outline'
                        "
                    />
                    <div
                        v-if="submission.modified !== submission.creation"
                        class="flex items-center text-ink-gray-5 text-sm gap-2"
                    >
                        <span> Modified {{ formatDateTime(submission.modified) }} </span>
                        <span>•</span>
                        <span> Created {{ formatDateTime(submission.creation) }} </span>
                    </div>
                    <div v-else class="text-ink-gray-5 text-sm">
                        <span> Created {{ formatDateTime(submission.creation) }} </span>
                    </div>
                </div>
            </div>
            <Button label="View" variant="outline" size="sm" class="text-sm" />
        </div>
    </div>
</template>
