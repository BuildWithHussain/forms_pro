<template>
    <div class="barcode-field-wrapper">
        <FormControl
            :model-value="barcodeValue"
            @update:model-value="handleInput"
            type="text"
            variant="outline"
            :placeholder="props.field.placeholder || 'Enter barcode value'"
        />
        <div v-if="barcodeValue" class="mt-4 border rounded-md p-4 bg-white flex justify-center">
            <svg ref="barcodeSvg" class="barcode-svg"></svg>
        </div>
        <p v-if="errorMessage" class="text-xs text-destructive mt-1">
            {{ errorMessage }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue';
import { FormControl } from 'frappe-ui';
import { FormField } from '@/types/formfield';
import JsBarcode from 'jsbarcode';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const barcodeValue = ref(props.modelValue || '');
const barcodeSvg = ref<SVGElement | null>(null);
const errorMessage = ref('');

watch(() => props.modelValue, (value) => {
    barcodeValue.value = value || '';
    if (value) {
        nextTick(() => generateBarcode(value));
    }
}, { immediate: true });

watch(barcodeValue, (value) => {
    if (value) {
        nextTick(() => generateBarcode(value));
    } else {
        errorMessage.value = '';
        if (barcodeSvg.value) {
            barcodeSvg.value.innerHTML = '';
        }
    }
});

onMounted(() => {
    if (barcodeValue.value && barcodeSvg.value) {
        generateBarcode(barcodeValue.value);
    }
});

function handleInput(value: string) {
    barcodeValue.value = value;
    emit('update:modelValue', value || null);
}

function generateBarcode(value: string) {
    if (!barcodeSvg.value || !value) return;
    
    try {
        errorMessage.value = '';
        const options: any = {
            fontSize: 16,
            width: 3,
            height: 50,
        };
        
        // Parse options from field.options if it's JSON
        if (props.field.options) {
            try {
                const parsedOptions = JSON.parse(props.field.options);
                Object.assign(options, parsedOptions);
            } catch {
                // Not JSON, use default options
            }
        }
        
        JsBarcode(barcodeSvg.value, value, options);
    } catch (error: any) {
        errorMessage.value = `Invalid Barcode: ${error.message || 'Invalid format'}`;
    }
}
</script>

<style scoped>
.barcode-svg {
    max-width: 100%;
    height: auto;
}
</style>

