<script setup lang="ts">
import { ErrorMessage, LoadingIndicator, Button } from "frappe-ui";
import { useSubmissionForm } from "@/stores/submissionForm";
import { computed } from "vue";
import FieldRenderer from "@/components/builder/FieldRenderer.vue";

const props = defineProps({
    themeColor: {
        type: String,
        default: '#3b82f6'
    }
});

const submissionFormStore = useSubmissionForm();

const buttonStyle = computed(() => {
    return {
        backgroundColor: props.themeColor,
        borderColor: props.themeColor
    };
});
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
                :theme-color="themeColor"
            />
        </div>
        <hr class="border-gray-200" />
        <ErrorMessage :message="submissionFormStore.errors.join('\n')" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
            <Button
                v-if="submissionFormStore.allowIncompleteForms"
                @click="submissionFormStore.saveAsDraft"
                :loading="submissionFormStore.isLoading"
                variant="outline"
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
                :style="buttonStyle"
            >
                Submit
            </Button>
        </div>
    </div>
</template>
