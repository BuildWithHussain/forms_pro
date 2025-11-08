<template>
    <div class="file-upload-field-wrapper">
        <!-- Label is rendered by FieldRenderer, so we don't render it here -->
        
        <div v-if="!selectedFile" class="file-upload-area border-2 border-dashed rounded-md p-4 text-center hover:border-primary transition-colors cursor-pointer bg-muted/50">
            <input
                ref="fileInput"
                type="file"
                class="hidden"
                @change="handleFileSelect"
                :accept="getAcceptTypes()"
            />
            <div @click="triggerFileSelect" class="flex flex-col items-center gap-2">
                <svg class="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-sm text-muted-foreground">
                    Click to upload or drag and drop
                </p>
                <p class="text-xs text-muted-foreground">
                    {{ getFileTypeHint() }}
                </p>
            </div>
        </div>
        
        <div v-else class="file-preview border rounded-md p-3 bg-background">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                    <svg class="w-5 h-5 text-muted-foreground flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium truncate">{{ selectedFile.name }}</p>
                        <p class="text-xs text-muted-foreground">{{ formatFileSize(selectedFile.size) }}</p>
                    </div>
                </div>
                <button
                    type="button"
                    @click="removeFile"
                    class="ml-2 p-1 hover:bg-muted rounded transition-colors"
                    aria-label="Remove file"
                >
                    <svg class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
        
        <p v-if="props.field.description" class="text-xs text-muted-foreground mt-1">
            {{ props.field.description }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: File | string | null; // Can be File object or base64 string
}>();

const emit = defineEmits<{
    'update:modelValue': [value: File | null];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
    if (newValue instanceof File) {
        selectedFile.value = newValue;
    } else if (!newValue) {
        selectedFile.value = null;
    }
    // If it's a base64 string, we don't set selectedFile as we can't reconstruct the File object
}, { immediate: true });

function triggerFileSelect() {
    fileInput.value?.click();
}

function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
        selectedFile.value = file;
        emit('update:modelValue', file);
    }
}

function removeFile() {
    selectedFile.value = null;
    if (fileInput.value) {
        fileInput.value.value = '';
    }
    emit('update:modelValue', null);
}

function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function getAcceptTypes(): string {
    // Check if field has options that specify file types
    if (props.field.options) {
        // Options might contain file type hints like "image/*", "application/pdf", etc.
        return props.field.options;
    }
    // Default: accept all files
    return '*/*';
}

function getFileTypeHint(): string {
    if (props.field.options) {
        const options = props.field.options.toLowerCase();
        if (options.includes('image')) {
            return 'Images only';
        }
        if (options.includes('pdf')) {
            return 'PDF files only';
        }
        if (options.includes('document') || options.includes('doc')) {
            return 'Documents only';
        }
    }
    return 'Any file type';
}
</script>

<style scoped>
.file-upload-area {
    min-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>

