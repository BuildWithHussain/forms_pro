<template>
    <div class="image-field-wrapper">
        <div v-if="!imageData" class="image-upload-area border-2 border-dashed rounded-md p-4 text-center hover:border-primary transition-colors cursor-pointer bg-muted/50">
            <input
                ref="fileInput"
                type="file"
                class="hidden"
                @change="handleFileSelect"
                accept="image/*"
            />
            <div @click="triggerFileSelect" class="flex flex-col items-center gap-2">
                <svg class="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-sm text-muted-foreground">
                    Click to upload an image
                </p>
                <p class="text-xs text-muted-foreground">
                    PNG, JPG, GIF up to 10MB
                </p>
            </div>
        </div>
        
        <div v-else class="image-preview border rounded-md p-3 bg-background">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                    <img :src="imageData" alt="Preview" class="h-16 w-16 object-cover rounded" />
                    <div>
                        <p class="text-sm font-medium">{{ imageName }}</p>
                        <p class="text-xs text-muted-foreground">{{ formatFileSize(imageSize) }}</p>
                    </div>
                </div>
                <Button variant="ghost" size="sm" @click="removeImage">
                    <X class="h-4 w-4" />
                </Button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-vue-next';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: File | string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: File | null];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const imageData = ref<string | null>(null);
const imageName = ref<string>('');
const imageSize = ref<number>(0);

// Initialize from modelValue
watch(() => props.modelValue, (value) => {
    if (value instanceof File) {
        loadFile(value);
    } else if (typeof value === 'string' && value.startsWith('data:')) {
        imageData.value = value;
        imageName.value = 'Image';
    } else if (value === null) {
        imageData.value = null;
        imageName.value = '';
        imageSize.value = 0;
    }
}, { immediate: true });

function triggerFileSelect() {
    fileInput.value?.click();
}

function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        const file = target.files[0];
        if (file.type.startsWith('image/')) {
            loadFile(file);
            emit('update:modelValue', file);
        }
    }
}

function loadFile(file: File) {
    imageName.value = file.name;
    imageSize.value = file.size;
    const reader = new FileReader();
    reader.onload = (e) => {
        imageData.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    imageData.value = null;
    imageName.value = '';
    imageSize.value = 0;
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
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
</script>

