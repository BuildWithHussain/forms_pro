<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from "vue";
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
const hasDrawn = ref(false); // Track if user has drawn something
const signatureData = ref<string | null>(props.modelValue || null);
const showCanvas = ref(!props.modelValue);

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
    signatureData.value = newValue || null;
    showCanvas.value = !newValue;
    if (newValue && canvasRef.value && !showCanvas.value) {
        // Only load if not in drawing mode
        loadSignatureFromData(newValue);
    }
});

// Initialize canvas with proper DPI handling
const initializeCanvas = () => {
    if (!canvasRef.value) return;
    
    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    // Set canvas drawing buffer size to match display size, scaled by DPR
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    // Scale the context to ensure drawing operations are at the correct resolution
    ctx.scale(dpr, dpr);

    // Set drawing style
    ctx.strokeStyle = "#000000";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    // Load existing signature if available
    if (props.modelValue && !showCanvas.value) {
        loadSignatureFromData(props.modelValue);
    } else {
        // Clear canvas if in drawing mode
        ctx.clearRect(0, 0, rect.width, rect.height);
    }
};

let resizeObserver: ResizeObserver | null = null;

// Initialize canvas on mount
onMounted(() => {
    initializeCanvas();
    
    // Re-initialize on resize
    resizeObserver = new ResizeObserver(() => {
        initializeCanvas();
        if (signatureData.value && !showCanvas.value) {
            loadSignatureFromData(signatureData.value);
        }
    });
    
    if (canvasRef.value) {
        resizeObserver.observe(canvasRef.value);
    }
});

onUnmounted(() => {
    if (resizeObserver && canvasRef.value) {
        resizeObserver.unobserve(canvasRef.value);
    }
});

// Load signature from base64 data
const loadSignatureFromData = (data: string) => {
    if (!canvasRef.value) return;
    
    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    const img = new Image();
    img.onload = () => {
        // Clear canvas
        ctx.clearRect(0, 0, rect.width, rect.height);
        
        // Calculate scaling to fit image within canvas bounds
        const scale = Math.min(
            rect.width / img.width,
            rect.height / img.height
        );
        const x = (rect.width - img.width * scale) / 2;
        const y = (rect.height - img.height * scale) / 2;
        
        ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
    };
    img.src = data;
};

// Start drawing
const startDrawing = (e: MouseEvent | TouchEvent) => {
    isDrawing.value = true;
    hasDrawn.value = true;
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

// Stop drawing (don't auto-save)
const stopDrawing = () => {
    if (isDrawing.value) {
        isDrawing.value = false;
    }
};

// Save signature as base64
const saveSignature = () => {
    if (!canvasRef.value || !hasDrawn.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Get the actual drawing area dimensions (accounting for DPR)
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    
    // Create a temporary canvas with the display size (not scaled by DPR) for export
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = rect.width;
    tempCanvas.height = rect.height;
    const tempCtx = tempCanvas.getContext("2d");
    if (!tempCtx) return;
    
    // Draw the current canvas content to the temp canvas, scaling down if needed
    tempCtx.drawImage(canvas, 0, 0, rect.width, rect.height);
    
    const dataURL = tempCanvas.toDataURL("image/png");
    signatureData.value = dataURL;
    emit("update:modelValue", dataURL);
    showCanvas.value = false;
};

// Clear current drawing (redo)
const clearDrawing = () => {
    if (!canvasRef.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    hasDrawn.value = false;
};

// Clear signature completely
const clearSignature = () => {
    if (!canvasRef.value) return;

    const canvas = canvasRef.value;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    signatureData.value = null;
    hasDrawn.value = false;
    emit("update:modelValue", null);
    showCanvas.value = true;
};

// Edit signature (show canvas again)
const editSignature = () => {
    showCanvas.value = true;
    hasDrawn.value = false; // Reset drawing state
    // Re-initialize canvas to ensure proper sizing
    setTimeout(() => {
        initializeCanvas();
        if (canvasRef.value && signatureData.value) {
            loadSignatureFromData(signatureData.value);
            hasDrawn.value = true; // Mark as having content
        }
    }, 0);
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
                <div class="flex gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        @click="clearDrawing"
                        :disabled="!hasDrawn"
                    >
                        <Trash2 class="mr-2 h-4 w-4" />
                        Redo
                    </Button>
                    <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        @click="clearSignature"
                    >
                        <Trash2 class="mr-2 h-4 w-4" />
                        Clear All
                    </Button>
                </div>
                <Button
                    type="button"
                    size="sm"
                    @click="saveSignature"
                    :disabled="!hasDrawn"
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

