<template>
    <div>
        <input
            ref="inputRef"
            type="file"
            :accept="acceptString"
            class="hidden"
            @change="onFileAdd"
        />
        <slot
            v-bind="{
                file,
                uploading,
                progress,
                uploaded,
                message,
                error,
                total,
                success,
                openFileSelector,
            }"
        >
            <Button @click="openFileSelector" :loading="uploading">
                {{ uploading ? `Uploading ${progress}%` : "Upload image" }}
            </Button>
        </slot>

        <!-- Crop dialog: Frappe UI -->
        <Dialog
            v-model="cropDialogOpen"
            :options="{
                title: 'Crop image',
                size: 'lg',
            }"
        >
            <template #body-content>
                <p class="text-sm text-ink-gray-6 mb-4">
                    Adjust the crop area to {{ cropDimensions.width }}×{{ cropDimensions.height }}
                    pixels, then upload.
                </p>
                <div class="cropper-container">
                    <Cropper
                        v-if="cropImageUrl"
                        ref="cropperRef"
                        :src="cropImageUrl"
                        :stencil-props="{
                            aspectRatio: cropDimensions.width / cropDimensions.height,
                        }"
                        :canvas="{
                            width: cropDimensions.width,
                            height: cropDimensions.height,
                        }"
                        image-restriction="stencil"
                        class="cropper"
                    />
                </div>
            </template>
            <template #actions="{ close }">
                <div class="flex justify-end gap-2">
                    <Button variant="ghost" label="Cancel" @click="close" />
                    <Button variant="outline" label="Reset" @click="onResetCrop" />
                    <Button
                        variant="solid"
                        label="Crop & Upload"
                        :loading="uploading"
                        :disabled="!cropperReady"
                        @click="onCropAndUpload"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { Cropper } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";
import { Button, Dialog, FileUploadHandler } from "frappe-ui";
import type { UploadOptions, UploadedFile } from "frappe-ui";

const props = withDefaults(
    defineProps<{
        cropDimensions: { width: number; height: number };
        fileTypes?: string | string[];
        uploadArgs?: UploadOptions;
        validateFile?: (file: File) => Promise<string | void>;
    }>(),
    {
        fileTypes: () => ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"],
    }
);

const emit = defineEmits<{
    success: [data: UploadedFile];
    failure: [error: unknown];
}>();

const acceptString = computed(() => {
    const types = props.fileTypes;
    if (typeof types === "string") return types;
    return Array.isArray(types) ? types.join(",") : "image/*";
});

const inputRef = ref<HTMLInputElement | null>(null);
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null);
const cropDialogOpen = ref(false);
const cropperReady = ref(false);

const file = ref<File | null>(null);
const uploading = ref(false);
const uploaded = ref(0);
const total = ref(0);
const error = ref<string | null>(null);
const message = ref("");
const finishedUploading = ref(false);
const cropImageUrl = ref<string | null>(null);
const pendingFileName = ref<string>("image.png");

const progress = computed(() => {
    const value = total.value ? Math.floor((uploaded.value / total.value) * 100) : 0;
    return Number.isNaN(value) ? 0 : value;
});

const success = computed(() => finishedUploading.value && !error.value);

function openFileSelector() {
    inputRef.value?.click();
}

function inputRefMethod() {
    return inputRef.value;
}

function revokeCropUrl() {
    if (cropImageUrl.value) {
        URL.revokeObjectURL(cropImageUrl.value);
        cropImageUrl.value = null;
    }
}

watch(cropDialogOpen, (open) => {
    if (!open) {
        revokeCropUrl();
        file.value = null;
        cropperReady.value = false;
    } else {
        cropperReady.value = true;
    }
});

async function onFileAdd(e: Event) {
    const target = e.target as HTMLInputElement;
    const selectedFile = target.files?.[0];
    target.value = "";

    error.value = null;
    file.value = selectedFile ?? null;

    if (!selectedFile) return;

    if (props.validateFile) {
        try {
            const msg = await props.validateFile(selectedFile);
            if (msg) {
                error.value = msg;
                return;
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : "Validation failed";
            return;
        }
    }

    revokeCropUrl();
    cropImageUrl.value = URL.createObjectURL(selectedFile);
    pendingFileName.value = selectedFile.name;
    cropperReady.value = false;
    cropDialogOpen.value = true;
}

function onResetCrop() {
    cropperRef.value?.reset();
}

async function onCropAndUpload() {
    const cropper = cropperRef.value;
    if (!cropper || !cropImageUrl.value) return;

    let result: { canvas?: HTMLCanvasElement };
    try {
        result = cropper.getResult();
    } catch {
        error.value = "Failed to get crop result";
        return;
    }

    const canvas = result.canvas;
    if (!canvas) {
        error.value = "Cropper did not return a canvas";
        return;
    }

    cropDialogOpen.value = false;
    revokeCropUrl();

    const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, "image/png", 1);
    });

    if (!blob) {
        error.value = "Failed to create image blob";
        return;
    }

    const croppedFile = new File([blob], pendingFileName.value.replace(/\.[^.]+$/, "") + ".png", {
        type: "image/png",
    });

    uploadFile(croppedFile);
}

function uploadFile(fileToUpload: File) {
    error.value = null;
    uploaded.value = 0;
    total.value = 0;
    finishedUploading.value = false;

    const uploader = new FileUploadHandler();
    uploader.on("start", () => {
        uploading.value = true;
    });
    uploader.on("progress", (data: { uploaded: number; total: number }) => {
        uploaded.value = data.uploaded;
        total.value = data.total;
    });
    uploader.on("error", () => {
        uploading.value = false;
        error.value = "Error Uploading File";
    });
    uploader.on("finish", () => {
        uploading.value = false;
        finishedUploading.value = true;
    });

    uploader
        .upload(fileToUpload, props.uploadArgs ?? {})
        .then((data: UploadedFile) => {
            emit("success", data);
        })
        .catch((err: unknown) => {
            uploading.value = false;
            let errorMessage = "Error Uploading File";
            const errorObj = err as { _server_messages?: string; exc?: string };
            if (errorObj?._server_messages) {
                try {
                    const parsed = JSON.parse(JSON.parse(errorObj._server_messages)[0]);
                    if (parsed?.message) errorMessage = parsed.message;
                } catch {
                    // keep default
                }
            } else if (errorObj?.exc) {
                try {
                    const lines = JSON.parse(errorObj.exc)[0]?.split("\n") ?? [];
                    const last = lines.slice(-2, -1)[0];
                    if (last) errorMessage = last;
                } catch {
                    // keep default
                }
            }
            error.value = errorMessage;
            emit("failure", err);
        });
}

defineExpose({
    openFileSelector,
    inputRef: inputRefMethod,
});
</script>

<style scoped>
.cropper-container {
    position: relative;
    width: 100%;
    max-width: 100%;
    height: 360px;
    overflow: hidden;
    background: var(--color-surface-gray-1, #f3f4f6);
    border-radius: 0.375rem;
}
.cropper-container :deep(.cropper),
.cropper-container :deep(.vue-advanced-cropper) {
    width: 100% !important;
    height: 100% !important;
    max-width: 100%;
    background: var(--color-surface-gray-1, #f3f4f6);
}
</style>
