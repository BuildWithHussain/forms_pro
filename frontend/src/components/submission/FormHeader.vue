<script setup lang="ts">
import { useSubmissionForm } from "@/stores/submissionForm";
import { LoadingIndicator } from "frappe-ui";

const submissionFormStore = useSubmissionForm();
</script>
<template>
    <div v-if="!submissionFormStore.formResource">
        <LoadingIndicator />
    </div>
    <div v-if="submissionFormStore.formResource.data" class="flex flex-col gap-4 text-gray-800">
        <h1 class="text-3xl font-bold">
            {{ submissionFormStore.formResource.data.title }}
        </h1>
        <div
            v-html="submissionFormStore.formResource.data.description"
            class="form-description !px-0"
        ></div>
        <hr />
    </div>
</template>
