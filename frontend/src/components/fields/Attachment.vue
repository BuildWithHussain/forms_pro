<script setup lang="ts">
import { ErrorMessage, FileUploader } from "frappe-ui";
import { ref } from "vue";

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["update:value"]);

// @ts-ignore
const value = defineModel<string>();

const inPreview = ref(false);

type FileType = {
    content_hash: string;
    creation: string;
    docstatus: number;
    doctype: string;
    file_name: string;
    file_size: number;
    file_type: string;
    file_url: string;
    folder: string;
    idx: number;
    is_attachments_folder: number;
    is_folder: number;
    is_home_folder: number;
    is_private: number;
    modified: string;
    modified_by: string;
    name: string;
    owner: string;
    uploaded_to_dropbox: number;
    uploaded_to_google_drive: number;
};

const fileData = ref<FileType | null>(null);

const formatFileSize = (fileSize: number) => {
    if (fileSize < 1024) return `${fileSize} B`;
    if (fileSize < 1024 * 1024) return `${(fileSize / 1024).toFixed(2)} KB`;
    if (fileSize < 1024 * 1024 * 1024) return `${(fileSize / 1024 / 1024).toFixed(2)} MB`;
    return `${(fileSize / 1024 / 1024 / 1024).toFixed(2)} GB`;
};

const handleChange = (file: FileType) => {
    fileData.value = file;
    if (file.file_url) {
        emit("update:value", file.file_url);
    }
    inPreview.value = true;
};

const handleRemove = () => {
    fileData.value = null;
    emit("update:value", "");
    inPreview.value = false;
};
</script>
<template>
    <div class="flex gap-2 flex-col mt-2">
        <FileUploader
            v-if="!inPreview"
            v-bind="props.field"
            @success="(file: FileType) => handleChange(file)"
        >
            <!-- @vue-ignore -->
            <template #default="{ uploading, progress, error, openFileSelector }">
                <Button @click="openFileSelector()" :loading="uploading">
                    {{ uploading ? `Uploading ${progress}%` : "Upload" }}
                </Button>
                <ErrorMessage :message="error" />
            </template>
        </FileUploader>
        <div v-if="inPreview" class="p-4 bg-white border rounded-md flex flex-col gap-2">
            <a :href="fileData?.file_url" target="_blank" class="text-sm font-medium">
                {{ fileData?.file_name }}
            </a>
            <span class="text-sm text-gray-500">
                {{ formatFileSize(fileData?.file_size || 0) }}
            </span>
            <Button
                theme="red"
                label="Remove"
                icon="trash"
                tooltip="Remove file"
                @click="handleRemove"
            />
        </div>
    </div>
</template>
