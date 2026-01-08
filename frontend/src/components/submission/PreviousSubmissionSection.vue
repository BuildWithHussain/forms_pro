<script setup lang="ts">
import { useSubmissionForm } from "@/stores/submissionForm";
import { Button } from "frappe-ui";
import { formatDateTime } from "@/utils/date";
import { Badge } from "frappe-ui";
import {
    AccordionContent,
    AccordionHeader,
    AccordionItem,
    AccordionRoot,
    AccordionTrigger,
} from "reka-ui";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

const submissionFormStore = useSubmissionForm();
const router = useRouter();
const selectedValue = ref<string | string[] | undefined>("previous-submissions");
const isOpen = computed(() => Boolean(selectedValue.value));
</script>
<template>
    <AccordionRoot v-model="selectedValue" class="form-container-simple" :collapsible="true">
        <AccordionItem value="previous-submissions">
            <AccordionHeader>
                <AccordionTrigger as="div" class="flex justify-between w-full cursor-pointer">
                    <div class="space-y-2">
                        <h2 class="text-2xl font-bold">Previous Submissions</h2>
                        <p class="text-base text-ink-gray-6">
                            Here are your previous submissions for this form.
                        </p>
                    </div>
                    <Button :icon="isOpen ? 'chevron-up' : 'chevron-down'" variant="outline" />
                </AccordionTrigger>
            </AccordionHeader>
            <AccordionContent as="div" class="space-y-4 mt-4">
                <div
                    v-for="(submission, index) in submissionFormStore.userSubmissions"
                    :key="submission.name"
                    class="flex justify-between w-full items-center border p-4 rounded-lg"
                >
                    <div class="text-lg font-medium space-y-2 flex flex-col">
                        <h4>Submission #{{ index + 1 }}</h4>

                        <div class="flex gap-2 items-center">
                            <Badge
                                v-if="submission.submission_status"
                                :label="submission.submission_status"
                                :variant="
                                    submission.submission_status === 'Submitted'
                                        ? 'subtle'
                                        : 'outline'
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
                    <Button
                        label="View"
                        variant="outline"
                        size="sm"
                        class="text-sm"
                        @click="
                            router.push(
                                `/p/${submissionFormStore.currentFormRoute}/edit/${submission.name}`
                            )
                        "
                    />
                </div>
            </AccordionContent>
        </AccordionItem>
    </AccordionRoot>
</template>
