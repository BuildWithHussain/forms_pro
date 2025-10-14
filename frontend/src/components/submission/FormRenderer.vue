<script setup lang="ts">
import { ErrorMessage, LoadingIndicator, Button } from "frappe-ui";
import { useSubmissionForm } from "@/stores/submissionForm";

const submissionFormStore = useSubmissionForm();
</script>
<template>
    <div v-if="submissionFormStore.isLoading">
        <LoadingIndicator class="mx-auto my-auto w-5 h-5" />
    </div>
    <div v-if="submissionFormStore.inFormSubmission" class="flex flex-col gap-4">
        <div v-for="field in submissionFormStore.formResource.data?.fields" :key="field.fieldname">
            <FieldRenderer
                v-model="submissionFormStore.fields[field.fieldname]"
                :field="field"
                :inEditMode="false"
            />
        </div>
        <hr />
        <ErrorMessage :message="submissionFormStore.errors.join('\n')" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
            <Button
                v-if="submissionFormStore.allowIncompleteForms"
                @click="submissionFormStore.saveAsDraft"
                :loading="submissionFormStore.isLoading"
            >
                Save as draft
            </Button>
            <Button
                variant="solid"
                @click="
                    () => {
                        submissionFormStore.submitForm();
                    }
                "
                :loading="submissionFormStore.isLoading"
            >
                Submit
            </Button>
        </div>
    </div>
</template>
