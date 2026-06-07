<script setup lang="ts">
import type { FormStep } from "@/composables/useFormSteps";
import { Check } from "@lucide/vue";

defineProps<{
    steps: FormStep[];
    currentIndex: number;
}>();

const emit = defineEmits<{
    "go-to": [index: number];
}>();
</script>

<template>
    <nav aria-label="Form steps" class="flex items-center gap-1">
        <template v-for="(step, idx) in steps" :key="idx">
            <button
                type="button"
                :aria-current="idx === currentIndex ? 'step' : undefined"
                :aria-label="`Step ${idx + 1}${step.label ? ': ' + step.label : ''}`"
                :disabled="idx > currentIndex"
                @click="idx <= currentIndex && emit('go-to', idx)"
                :class="[
                    'flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm transition-colors',
                    idx === currentIndex && 'bg-surface-gray-6 text-ink-white',
                    idx < currentIndex &&
                        'bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3 cursor-pointer',
                    idx > currentIndex && 'bg-surface-gray-1 text-ink-gray-4 cursor-default',
                ]"
            >
                <span
                    :class="[
                        'w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium shrink-0',
                        idx === currentIndex && 'bg-ink-white/20',
                        idx < currentIndex && 'bg-surface-gray-4 text-ink-white',
                        idx > currentIndex && 'bg-surface-gray-2',
                    ]"
                >
                    <Check v-if="idx < currentIndex" class="w-3 h-3" />
                    <template v-else>{{ idx + 1 }}</template>
                </span>
                <span v-if="step.label" class="hidden sm:inline truncate max-w-32">
                    {{ step.label }}
                </span>
            </button>
            <div
                v-if="idx < steps.length - 1"
                :class="[
                    'w-6 h-px',
                    idx < currentIndex ? 'bg-surface-gray-4' : 'bg-outline-gray-2',
                ]"
            />
        </template>
    </nav>
</template>
