<script setup lang="ts">
import { ErrorMessage, LoadingIndicator, Button } from "frappe-ui";
import { useSubmissionForm } from "@/stores/submissionForm";
import FieldRenderer from "@/components/builder/FieldRenderer.vue";
import { computed } from "vue";
import { shouldFieldBeVisible, shouldFieldBeRequired } from "@/utils/conditionals";
import { useGroupedRows } from "@/composables/useGroupedRows";
import type { FormField } from "@/types/formfield";

const submissionFormStore = useSubmissionForm();

const props = withDefaults(
    defineProps<{
        disabled: boolean;
    }>(),
    {
        disabled: false,
    }
);

const allFields = computed<FormField[]>(() => submissionFormStore.formResource.data?.fields || []);

const groupedRows = useGroupedRows(allFields);

function isFieldVisible(field: FormField) {
    return shouldFieldBeVisible(field, submissionFormStore.fields, allFields.value);
}

function handleSubmitForm() {
    submissionFormStore.submitForm();
}
</script>
<template>
    <div v-if="submissionFormStore.isLoading">
        <LoadingIndicator class="mx-auto my-auto w-5 h-5" />
    </div>
    <div v-if="submissionFormStore.inFormFillingState" class="flex flex-col gap-4">
        <template v-for="(row, rIdx) in groupedRows" :key="`r-${row[0]?.row_index ?? rIdx}`">
            <div v-if="row.some(isFieldVisible)" class="flex flex-col md:flex-row gap-4">
                <template v-for="field in row" :key="field.fieldname">
                    <div v-if="isFieldVisible(field)" class="flex-1 min-w-0">
                        <FieldRenderer
                            :disabled="disabled"
                            v-model="submissionFormStore.fields[field.fieldname]"
                            :field="{
                                ...field,
                                reqd: shouldFieldBeRequired(
                                    field,
                                    submissionFormStore.fields,
                                    allFields
                                ),
                            }"
                            :inEditMode="false"
                        />
                    </div>
                </template>
            </div>
        </template>
        <hr />
        <ErrorMessage :message="submissionFormStore.errors.join('\n')" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
            <slot name="actions">
                <Button
                    v-if="submissionFormStore.allowIncompleteForms"
                    @click="submissionFormStore.saveAsDraft"
                    :loading="submissionFormStore.isLoading"
                >
                    Save as draft
                </Button>
                <Button
                    variant="solid"
                    @click="handleSubmitForm"
                    :loading="submissionFormStore.isLoading"
                >
                    Submit
                </Button>
            </slot>
        </div>
    </div>
</template>
