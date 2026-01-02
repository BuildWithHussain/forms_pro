<script setup lang="ts">
import { useRoute } from "vue-router";
import { useSubmissionForm } from "@/stores/submissionForm";
import FormHeader from "@/components/submission/FormHeader.vue";
import FormRenderer from "@/components/submission/FormRenderer.vue";
import Logo from "@/assets/Logo.vue";
import PageHeader from "@/components/submission/PageHeader.vue";

const route = useRoute();
const submissionFormStore = useSubmissionForm();
submissionFormStore.initialize(route.params.route as string);
</script>
<template>
    <div class="p-8">
        <PageHeader />

        <div
            class="space-y-4 shadow-[0_0_10px_0_rgba(0,0,0,0.1)] bg-secondary border rounded-lg p-6 max-w-screen-md mx-auto mt-16"
        >
            <div class="space-y-4" v-if="submissionFormStore.inFormSubmission">
                <FormHeader />
                <FormRenderer />
            </div>
            <SuccessSection v-if="submissionFormStore.successSubmission" />
        </div>

        <div class="z-10 absolute bottom-0 right-0 p-8">
            <div class="flex flex-col items-end text-ink-gray-8">
                <span class="text-xs">Built on</span>
                <a
                    href="https://github.com/buildwithhussain/forms_pro"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <Logo class="font-normal" />
                </a>
            </div>
        </div>
    </div>
</template>
