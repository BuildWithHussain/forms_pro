<script setup lang="ts">
import { ErrorMessage, LoadingIndicator, Button } from "frappe-ui";
import { useSubmissionForm } from "@/stores/submissionForm";
import FieldRenderer from "@/components/builder/FieldRenderer.vue";
import { computed } from "vue";
import { shouldFieldBeVisible, shouldFieldBeRequired } from "@/utils/conditionals";
import { useGroupedRows } from "@/composables/useGroupedRows";
import type { FormField } from "@/types/formfield";
import { ArrowRight } from "@lucide/vue";

const store = useSubmissionForm();

const props = withDefaults(
    defineProps<{
        disabled: boolean;
    }>(),
    {
        disabled: false,
    }
);

const allFields = computed<FormField[]>(() => store.formResource.data?.fields || []);

const stepFields = computed<FormField[]>(() => store.currentStepFields);
const groupedRows = useGroupedRows(stepFields);

const animClass = computed(() => {
    return store.stepDirection === "forward" ? "anim-forward" : "anim-back";
});

function isFieldVisible(field: FormField) {
    return shouldFieldBeVisible(field, store.fields, allFields.value);
}

function rowKey(row: FormField[][], rIdx: number) {
    return `r-${row[0]?.[0]?.row_index ?? rIdx}`;
}

function colKey(col: FormField[], cIdx: number) {
    return `c-${col[0]?.column_index ?? cIdx}`;
}
</script>
<template>
    <div v-if="store.isLoading">
        <LoadingIndicator class="mx-auto my-auto w-5 h-5" />
    </div>
    <div v-if="store.inFormFillingState" class="flex flex-col overflow-hidden">
        <!-- Fields (enter-only animation on step change) -->
        <div :key="store.currentStepIndex" :class="animClass" class="flex flex-col gap-4">
            <template v-for="(row, rIdx) in groupedRows" :key="rowKey(row, rIdx)">
                <div
                    v-if="row.some((col) => col.some(isFieldVisible))"
                    class="flex flex-col md:flex-row gap-4"
                    data-form-renderer-component="form-row"
                >
                    <template v-for="(col, cIdx) in row" :key="colKey(col, cIdx)">
                        <div
                            v-if="col.some(isFieldVisible)"
                            class="flex flex-col gap-4 flex-1 min-w-0"
                            data-form-renderer-component="form-column"
                        >
                            <template v-for="field in col" :key="field.fieldname">
                                <div v-if="isFieldVisible(field)">
                                    <FieldRenderer
                                        :disabled="disabled"
                                        v-model="store.fields[field.fieldname]"
                                        :field="{
                                            ...field,
                                            reqd: shouldFieldBeRequired(
                                                field,
                                                store.fields,
                                                allFields
                                            ),
                                        }"
                                        :inEditMode="false"
                                    />
                                </div>
                            </template>
                        </div>
                    </template>
                </div>
            </template>
        </div>

        <hr class="mt-4" />
        <ErrorMessage :message="store.errors.join('\n')" class="mt-4" />

        <!-- Footer: progress pills left, buttons right -->
        <div class="flex items-center justify-between mt-4">
            <!-- Progress pills -->
            <div v-if="store.isMultiStep" class="flex items-center gap-1.5">
                <div
                    v-for="idx in store.totalSteps"
                    :key="idx"
                    class="h-[5px] rounded-full transition-all duration-[280ms] ease-[cubic-bezier(0.4,0,0.2,1)]"
                    :class="{
                        'w-1.5 bg-surface-gray-5': idx - 1 < store.currentStepIndex,
                        'w-5 bg-surface-gray-7': idx - 1 === store.currentStepIndex,
                        'w-1.5 bg-surface-gray-3': idx - 1 > store.currentStepIndex,
                    }"
                />
            </div>
            <div v-else />

            <slot name="actions">
                <div class="grid grid-flow-col gap-2 w-3/5">
                    <Button v-if="store.isMultiStep && !store.isFirstStep" @click="store.prevStep">
                        Back
                    </Button>
                    <Button
                        v-if="store.allowIncompleteForms && store.isLastStep"
                        @click="store.saveAsDraft"
                        :loading="store.isLoading"
                    >
                        Save as draft
                    </Button>
                    <Button
                        v-if="!store.isLastStep"
                        variant="solid"
                        @click="store.handleNextStep"
                        :loading="store.isLoading"
                    >
                        <span class="flex items-center gap-1.5">
                            Next
                            <ArrowRight class="w-3.5 h-3.5" :stroke-width="2.2" />
                        </span>
                    </Button>
                    <Button
                        v-else
                        variant="solid"
                        @click="store.submitForm()"
                        :loading="store.isLoading"
                    >
                        Submit
                    </Button>
                </div>
            </slot>
        </div>
    </div>
</template>

<style scoped>
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(22px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-22px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.anim-forward {
    animation: slideInRight 0.22s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

.anim-back {
    animation: slideInLeft 0.22s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
</style>
