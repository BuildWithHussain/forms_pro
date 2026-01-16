<script setup lang="ts">
import { DotLottieVue } from "@lottiefiles/dotlottie-vue";
import { useSubmissionForm } from "@/stores/submissionForm";
import { computed } from "vue";
import { TextEditor } from "frappe-ui";

const submissionFormStore = useSubmissionForm();

const successTitle = computed(() => {
    if (!submissionFormStore.formResource.data?.success_title) {
        return "Form submitted successfully";
    }
    return submissionFormStore.formResource.data.success_title;
});

const successDescription = computed(() => {
    if (!submissionFormStore.formResource.data?.success_description) {
        return "Thank you for submitting the form. We will get back to you soon.";
    }
    return submissionFormStore.formResource.data.success_description;
});
</script>
<template>
    <div class="flex flex-col gap-4 items-center">
        <DotLottieVue
            src="https://lottie.host/b9ba5ce8-d753-497a-946c-76e0da2ec22d/QcoLWNS7AP.lottie"
            autoplay
            :loop="false"
            :height="150"
            class="h-[150px]"
        />
        <h2 class="text-3xl font-bold">{{ successTitle }}</h2>
        <TextEditor
            :model-value="successDescription"
            editor-class="h-fit !w-full form-description !px-0 max-w-full max-h-full"
            :editable="false"
        />
    </div>
</template>
