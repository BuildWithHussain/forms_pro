<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { Button } from "@/components/ui/button";
import { Trash2, Pen } from "lucide-vue-next";

const props = defineProps<{
    modelValue?: string | null;
    field?: any;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: string | null];
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
const isDrawing = ref(false);
const signatureData = ref<string | null>(props.modelValue || null);
const showCanvas = ref(!props.modelValue);

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
    signatureData.value = newValue || null;
    showCanvas.value = !newValue;
    if (newValue && canvasRef.value) {
        loadSignatureFromData(newValue);
    }
});

// Initialize canvas
onMounted(() => {
    if (canvasRef.value) {
        const canvas = canvasRef.value;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Set canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;

        // Set drawing style
        ctx.strokeStyle = "#000000";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";

        // Load existing signature if available
        if (props.modelValue) {
            loadSignatureFromData(props.modelValue);
            showCanvas.value = false;
        }
    }
});

// Load signature from base64 data
const loadSignatureFromData = (data: string) => {
    if (!canvasRef.value) return;
    
    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    };
    img.src = data;
};

// Start drawing
const startDrawing = (e: MouseEvent | TouchEvent) => {
    isDrawing.value = true;
    const canvas = canvasRef.value;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e as MouseEvent).clientX ? (e as MouseEvent).clientX - rect.left : (e as TouchEvent).touches[0].clientX - rect.left;
    const y = (e as MouseEvent).clientY ? (e as MouseEvent).clientY - rect.top : (e as TouchEvent).touches[0].clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(x, y);
};

// Draw
const draw = (e: MouseEvent | TouchEvent) => {
    if (!isDrawing.value || !canvasRef.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e as MouseEvent).clientX ? (e as MouseEvent).clientX - rect.left : (e as TouchEvent).touches[0].clientX - rect.left;
    const y = (e as MouseEvent).clientY ? (e as MouseEvent).clientY - rect.top : (e as TouchEvent).touches[0].clientY - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
};

// Stop drawing
const stopDrawing = () => {
    if (isDrawing.value && canvasRef.value) {
        isDrawing.value = false;
        saveSignature();
    }
};

// Save signature as base64
const saveSignature = () => {
    if (!canvasRef.value) return;

    const canvas = canvasRef.value;
    const dataURL = canvas.toDataURL("image/png");
    signatureData.value = dataURL;
    emit("update:modelValue", dataURL);
    showCanvas.value = false;
};

// Clear signature
const clearSignature = () => {
    if (!canvasRef.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    signatureData.value = null;
    emit("update:modelValue", null);
    showCanvas.value = true;
};

// Edit signature (show canvas again)
const editSignature = () => {
    showCanvas.value = true;
    if (canvasRef.value && signatureData.value) {
        loadSignatureFromData(signatureData.value);
    }
};
</script>

<template>
    <div class="signature-field w-full">
        <!-- Canvas for drawing signature -->
        <div v-if="showCanvas" class="border rounded-md p-4 bg-white">
            <canvas
                ref="canvasRef"
                class="w-full border rounded cursor-crosshair touch-none"
                style="height: 300px;"
                @mousedown="startDrawing"
                @mousemove="draw"
                @mouseup="stopDrawing"
                @mouseleave="stopDrawing"
                @touchstart="startDrawing"
                @touchmove="draw"
                @touchend="stopDrawing"
            ></canvas>
            <div class="flex items-center justify-between mt-4 gap-2">
                <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    @click="clearSignature"
                >
                    <Trash2 class="mr-2 h-4 w-4" />
                    Clear
                </Button>
                <Button
                    type="button"
                    size="sm"
                    @click="saveSignature"
                    :disabled="!signatureData"
                >
                    Save Signature
                </Button>
            </div>
        </div>

        <!-- Display saved signature -->
        <div v-else class="border rounded-md p-4 bg-white">
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <img
                        v-if="signatureData"
                        :src="signatureData"
                        alt="Signature"
                        class="max-h-32 border rounded bg-white p-2"
                    />
                    <p v-else class="text-sm text-muted-foreground">No signature</p>
                </div>
                <div class="flex gap-2 ml-4">
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        @click="editSignature"
                    >
                        <Pen class="mr-2 h-4 w-4" />
                        Edit
                    </Button>
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        @click="clearSignature"
                    >
                        <Trash2 class="mr-2 h-4 w-4" />
                        Clear
                    </Button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.signature-field canvas {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}

.signature-field canvas:active {
    cursor: crosshair;
}
</style>

