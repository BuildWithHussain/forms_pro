<script setup lang="ts">
import PageHeader from "@/components/submission/PageHeader.vue";
import { Alert, Badge, LoadingText, Button } from "frappe-ui";
import { useRoute } from "vue-router";
import { useSubmissionForm } from "@/stores/submissionForm";
import { useEditSubmission } from "@/stores/editSubmission";
import { computed, watch } from "vue";
import FormRenderer from "@/components/submission/FormRenderer.vue";
import { CircleDashed } from "lucide-vue-next";
import { formatDateTime } from "@/utils/date";

const route = useRoute();
const submissionFormStore = useSubmissionForm();
const editSubmissionStore = useEditSubmission();

submissionFormStore.initialize(route.params.route as string);
watch(
    () => submissionFormStore.formResource.data,
    () => {
        if (submissionFormStore.formResource.data) {
            editSubmissionStore.initialize(
                submissionFormStore.formResource.data?.linked_doctype,
                route.params.submissionName as string
            );
        }
    },
    { immediate: true }
);

watch(
    () => editSubmissionStore.submission,
    () => {
        if (editSubmissionStore.submission) {
            Object.keys(submissionFormStore.fields).forEach((key) => {
                const matchingField = editSubmissionStore.submission[key];
                if (matchingField !== undefined) {
                    submissionFormStore.fields[key] = matchingField;
                }
            });
        }
    },
    { immediate: true }
);

const isDirty = computed(() => {
    return Object.keys(submissionFormStore.fields).some((key) => {
        return submissionFormStore.fields[key] !== editSubmissionStore.submission[key];
    });
});
</script>
<template>
    <LoadingText v-if="editSubmissionStore.isLoading" class="mx-auto my-auto w-5 h-5" />
    <div v-else>
        <div class="p-8 bg-surface-gray-1 min-h-svh space-y-12">
            <PageHeader />
            <div class="mx-auto max-w-screen-md space-y-6">
                <Button
                    label="Go to Submission Page"
                    icon-left="arrow-left"
                    variant="ghost"
                    @click="$router.push(`/p/${submissionFormStore.formResource.data?.route}`)"
                />
                <div class="space-y-3">
                    <h2 class="text-lg font-bold">Edit Submission</h2>
                    <h3 class="text-xl font-medium">
                        {{ submissionFormStore.formResource.data?.title }}
                    </h3>
                    <Badge
                        variant="subtle"
                        :label="submissionFormStore.formIsPublished ? 'Live' : 'Closed'"
                        :theme="submissionFormStore.formIsPublished ? 'green' : 'red'"
                    />
                </div>
                <hr />
                <div class="space-y-3">
                    <h3 class="text-lg font-medium">Submission Details</h3>
                    <div class="flex gap-2 items-center text-sm text-ink-gray-6">
                        <span>Status</span>
                        <Badge
                            :variant="editSubmissionStore.isDraft ? 'outline' : 'solid'"
                            :label="editSubmissionStore.submission?.fp_submission_status"
                        />
                    </div>
                    <div class="text-sm text-ink-gray-6">
                        Submission ID:
                        <span class="font-mono">
                            {{ editSubmissionStore.submission?.name }}
                        </span>
                    </div>
                    <div class="flex gap-2 items-center text-sm text-ink-gray-6">
                        <span
                            >Last Modified:
                            {{ formatDateTime(editSubmissionStore.submission?.modified) }}</span
                        >
                        <span>•</span>
                        <span
                            >Created:
                            {{ formatDateTime(editSubmissionStore.submission?.creation) }}</span
                        >
                    </div>
                </div>
                <Alert
                    v-if="!submissionFormStore.formIsPublished"
                    :dismissable="false"
                    title="Form is closed!"
                    theme="blue"
                    description="This form is no longer live. You can no longer edit your submission."
                />
                <div class="form-container-simple">
                    <FormRenderer :disabled="!submissionFormStore.formIsPublished">
                        <template #actions>
                            <div v-if="!submissionFormStore.formIsPublished">
                                <span class="text-xs">
                                    Actions are disabled because the form is no longer live.
                                </span>
                            </div>
                            <template v-else>
                                <Button
                                    v-if="editSubmissionStore.isDraft && isDirty"
                                    label="Update"
                                    @click="
                                        () => {
                                            submissionFormStore.validateValues();
                                            if (submissionFormStore.errors.length > 0) {
                                                return;
                                            }
                                            editSubmissionStore.updateForm(
                                                submissionFormStore.fields
                                            );
                                        }
                                    "
                                    :loading="editSubmissionStore.submissionResource.loading"
                                />
                                <Button
                                    v-if="editSubmissionStore.isDraft && !isDirty"
                                    label="Submit"
                                    :disabled="isDirty"
                                    variant="solid"
                                    @click="
                                        () => {
                                            submissionFormStore.validateValues();
                                            if (submissionFormStore.errors.length > 0) {
                                                return;
                                            }
                                            editSubmissionStore.submitForm();
                                        }
                                    "
                                    :loading="editSubmissionStore.submissionResource.loading"
                                    :tooltip="
                                        isDirty
                                            ? 'You have unsaved changes. Please update the form before submitting.'
                                            : ''
                                    "
                                />
                                <Button
                                    v-if="editSubmissionStore.isSubmitted"
                                    label="Convert to draft"
                                    :icon-left="CircleDashed"
                                    @click="editSubmissionStore.convertToDraft"
                                />
                                <Button
                                    v-if="editSubmissionStore.isSubmitted"
                                    variant="solid"
                                    @click="
                                        editSubmissionStore.updateAndSubmitForm(
                                            submissionFormStore.fields
                                        )
                                    "
                                    :disabled="!isDirty"
                                    :loading="submissionFormStore.isLoading"
                                    :tooltip="!isDirty ? 'No changes to Update' : ''"
                                >
                                    Update & Submit
                                </Button>
                            </template>
                        </template>
                    </FormRenderer>
                </div>
            </div>
        </div>
    </div>
</template>
