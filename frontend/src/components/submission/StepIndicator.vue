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
    <nav aria-label="Form steps" class="w-full overflow-x-auto">
        <div class="flex items-start w-max mx-auto px-1">
            <template v-for="(step, idx) in steps" :key="idx">
                <!-- Step node -->
                <div
                    class="flex flex-col items-center gap-2 select-none shrink-0 min-w-[60px] max-w-[96px]"
                    :class="idx < currentIndex ? 'cursor-pointer' : 'cursor-default'"
                    @click="idx < currentIndex && emit('go-to', idx)"
                >
                    <!-- Circle -->
                    <div
                        class="relative z-10 flex items-center justify-center shrink-0 w-8 h-8 rounded-full border-2 transition-[background-color,border-color] duration-200 ease-out"
                        :class="{
                            'bg-surface-gray-7 border-outline-gray-4': idx <= currentIndex,
                            'bg-transparent border-outline-gray-3': idx > currentIndex,
                            'shadow-[0_0_0_5px_rgba(10,10,10,0.08)]': idx === currentIndex,
                        }"
                    >
                        <Check
                            v-if="idx < currentIndex"
                            class="w-3 h-3 text-ink-white animate-check-in"
                            :stroke-width="2.5"
                        />
                        <span
                            v-else
                            class="text-xs font-bold leading-none"
                            :class="idx === currentIndex ? 'text-ink-white' : 'text-ink-gray-4'"
                        >
                            {{ idx + 1 }}
                        </span>
                    </div>
                    <!-- Label + field count -->
                    <div class="flex flex-col items-center gap-0.5">
                        <span
                            v-if="step.label"
                            class="block max-w-[88px] truncate text-center text-[11.5px] transition-colors duration-200 ease-out"
                            :class="{
                                'font-semibold text-ink-gray-9': idx === currentIndex,
                                'font-medium text-ink-gray-5': idx < currentIndex,
                                'text-ink-gray-4': idx > currentIndex,
                            }"
                        >
                            {{ step.label }}
                        </span>
                        <span
                            class="text-[10.5px] tabular-nums text-ink-gray-4"
                            :style="{ opacity: idx === currentIndex ? 0.9 : 0.55 }"
                        >
                            {{ step.fields.length }}
                            field{{ step.fields.length !== 1 ? "s" : "" }}
                        </span>
                    </div>
                </div>

                <!-- Connector -->
                <div
                    v-if="idx < steps.length - 1"
                    class="w-10 sm:w-16 relative overflow-hidden h-0.5 mt-[15px] rounded-sm bg-surface-gray-2"
                >
                    <div
                        class="absolute inset-0 bg-surface-gray-7 origin-left transition-transform duration-[400ms] ease-[cubic-bezier(0.4,0,0.2,1)]"
                        :style="{
                            transform: `scaleX(${idx < currentIndex ? 1 : 0})`,
                        }"
                    />
                </div>
            </template>
        </div>
    </nav>
</template>

<style scoped>
@keyframes check-in {
    from {
        opacity: 0;
        transform: scale(0.5);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.animate-check-in {
    animation: check-in 200ms ease-out;
}
</style>
