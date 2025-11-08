<template>
    <div class="duration-field-wrapper">
        <div class="flex items-center gap-2">
            <FormControl
                v-model.number="hours"
                type="number"
                variant="outline"
                placeholder="0"
                :min="0"
                class="w-20"
            />
            <span class="text-sm text-muted-foreground">h</span>
            <FormControl
                v-model.number="minutes"
                type="number"
                variant="outline"
                placeholder="0"
                :min="0"
                :max="59"
                class="w-20"
            />
            <span class="text-sm text-muted-foreground">m</span>
            <FormControl
                v-model.number="seconds"
                type="number"
                variant="outline"
                placeholder="0"
                :min="0"
                :max="59"
                class="w-20"
            />
            <span class="text-sm text-muted-foreground">s</span>
        </div>
        <p v-if="totalSeconds > 0" class="text-xs text-muted-foreground mt-1">
            Total: {{ formatDuration(totalSeconds) }}
        </p>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { FormControl } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: number | string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: number | null];
}>();

const hours = ref(0);
const minutes = ref(0);
const seconds = ref(0);

// Parse duration from modelValue (in seconds)
watch(() => props.modelValue, (value) => {
    if (value === null || value === undefined || value === '') {
        hours.value = 0;
        minutes.value = 0;
        seconds.value = 0;
        return;
    }
    const totalSecs = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(totalSecs)) return;
    
    hours.value = Math.floor(totalSecs / 3600);
    minutes.value = Math.floor((totalSecs % 3600) / 60);
    seconds.value = Math.floor(totalSecs % 60);
}, { immediate: true });

const totalSeconds = computed(() => {
    return hours.value * 3600 + minutes.value * 60 + seconds.value;
});

watch([hours, minutes, seconds], () => {
    emit('update:modelValue', totalSeconds.value > 0 ? totalSeconds.value : null);
});

function formatDuration(totalSeconds: number): string {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    
    const parts: string[] = [];
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    if (s > 0) parts.push(`${s}s`);
    
    return parts.length > 0 ? parts.join(' ') : '0s';
}
</script>

