<script setup lang="ts">
import { useSubmissionForm } from "@/stores/submissionForm";
import { LoadingIndicator } from "frappe-ui";
import { computed } from "vue";

const props = defineProps({
    themeColor: {
        type: String,
        default: '#3b82f6'
    }
});

const submissionFormStore = useSubmissionForm();

const titleStyle = computed(() => {
    return {
        color: props.themeColor
    };
});
</script>
<template>
    <div v-if="!submissionFormStore.formResource">
        <LoadingIndicator />
    </div>
    <div v-if="submissionFormStore.formResource.data" class="flex flex-col gap-4">
        <h1 class="text-3xl font-bold" :style="titleStyle">
            {{ submissionFormStore.formResource.data?.title ?? "" }}
        </h1>
        <div
            v-html="submissionFormStore.formResource.data?.description"
            class="form-description text-gray-700"
        ></div>
        <hr class="border-gray-200" />
    </div>
</template>
