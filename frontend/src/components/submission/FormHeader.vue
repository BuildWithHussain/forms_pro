<script setup lang="ts">
import { useSubmissionForm } from "@/stores/submissionForm";
import { LoadingIndicator, TextEditor } from "frappe-ui";
import { ArrowLeft } from "@lucide/vue";

const store = useSubmissionForm();
</script>
<template>
    <div v-if="!store.formResource">
        <LoadingIndicator />
    </div>

    <!-- Step 2+ compact header (multi-step only) -->
    <div
        v-else-if="store.isMultiStep && !store.isFirstStep && store.formResource.data"
        class="flex items-center gap-3 pb-4 border-b border-outline-gray-1"
    >
        <button
            @click="store.prevStep"
            class="flex items-center justify-center w-[30px] h-[30px] shrink-0 rounded-lg border border-outline-gray-2 bg-surface-white text-ink-gray-4 hover:border-outline-gray-4 active:scale-95 transition-[border-color,transform] duration-150 cursor-pointer"
        >
            <ArrowLeft class="w-3.5 h-3.5" :stroke-width="2.2" />
        </button>
        <div class="flex-1 min-w-0">
            <div class="text-[10.5px] text-ink-gray-4 font-medium tracking-wider uppercase mb-0.5">
                Step {{ store.currentStepIndex + 1 }} of {{ store.totalSteps }}
            </div>
            <h2 class="text-[17px] font-bold text-ink-gray-9 tracking-tight truncate">
                {{ store.steps[store.currentStepIndex]?.label || "Details" }}
            </h2>
        </div>
        <div
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-gray-2 text-[11px] font-semibold text-ink-gray-5 tabular-nums shrink-0"
        >
            {{ store.currentStepFields.length }}
            field{{ store.currentStepFields.length !== 1 ? "s" : "" }}
        </div>
    </div>

    <!-- Default full header (step 1 or single-step) -->
    <div v-else-if="store.formResource.data" class="flex flex-col gap-4 text-ink-gray-8">
        <h1 class="text-3xl font-bold">
            {{ store.formResource.data.title }}
        </h1>
        <TextEditor
            :content="store.formResource.data?.description"
            editor-class="h-fit !w-full form-description !px-0 max-w-full max-h-full"
            :editable="false"
        />
        <hr />
    </div>
</template>
