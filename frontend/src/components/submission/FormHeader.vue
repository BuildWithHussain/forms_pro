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

// Get font family from form data
const fontFamily = computed(() => {
    const font = submissionFormStore.formResource?.data?.font_family || 'System Default';
    if (font === 'System Default') {
        return '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    }
    return font;
});

// Get logo URL
const getImageUrl = (filePath: string | null | undefined): string => {
    if (!filePath) return '';
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        return filePath;
    }
    if (filePath.startsWith('/files/')) {
        return filePath;
    }
    let cleanPath = filePath;
    if (cleanPath.startsWith('files/')) {
        cleanPath = cleanPath.substring(6);
    }
    if (cleanPath.startsWith('/')) {
        cleanPath = cleanPath.substring(1);
    }
    return `/files/${cleanPath}`;
};

const logoUrl = computed(() => {
    const logo = submissionFormStore.formResource?.data?.logo;
    if (!logo) return null;
    return getImageUrl(logo);
});
</script>
<template>
    <div v-if="!submissionFormStore.formResource">
        <LoadingIndicator />
    </div>
    <div v-if="submissionFormStore.formResource.data" class="flex flex-col gap-4" :style="{ fontFamily: fontFamily }">
        <div class="flex items-start justify-between gap-4">
            <h1 class="text-3xl font-bold flex-1" :style="titleStyle">
                {{ submissionFormStore.formResource.data?.title ?? "" }}
            </h1>
            <img 
                v-if="logoUrl"
                :src="logoUrl"
                alt="Logo"
                class="max-w-[150px] max-h-[60px] object-contain"
                style="flex-shrink: 0;"
            />
        </div>
        <div
            v-html="submissionFormStore.formResource.data?.description"
            class="form-description text-gray-700"
        ></div>
        <hr class="border-gray-200" />
    </div>
</template>
