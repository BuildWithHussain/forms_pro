<script setup lang="ts">
import { computed } from "vue";
import type { FormStep } from "@/composables/useFormSteps";
import { Check } from "@lucide/vue";

const props = defineProps<{
    steps: FormStep[];
    currentIndex: number;
}>();

const emit = defineEmits<{
    "go-to": [index: number];
}>();

const stepperWidth = computed(() => {
    const pct = Math.min(100, (props.steps.length - 1) * 20);
    return `${pct}%`;
});
</script>

<template>
    <nav aria-label="Form steps" class="flex flex-col items-center w-full">
        <div class="flex items-start" :style="{ width: stepperWidth }">
            <template v-for="(step, idx) in steps" :key="idx">
                <!-- Step node -->
                <div
                    class="flex flex-col items-center gap-2 select-none min-w-[72px]"
                    :class="idx < currentIndex ? 'cursor-pointer' : 'cursor-default'"
                    @click="idx < currentIndex && emit('go-to', idx)"
                >
                    <!-- Circle -->
                    <div
                        class="relative z-10 flex items-center justify-center shrink-0 w-8 h-8 rounded-full border-2 transition-[background-color,border-color] duration-200 ease-out"
                        :class="{
                            'bg-gray-900 border-gray-900': idx <= currentIndex,
                            'bg-transparent border-gray-400': idx > currentIndex,
                            'shadow-[0_0_0_5px_rgba(10,10,10,0.08)]': idx === currentIndex,
                        }"
                    >
                        <Check
                            v-if="idx < currentIndex"
                            class="w-3 h-3 text-white animate-check-in"
                            :stroke-width="2.5"
                        />
                        <span
                            v-else
                            class="text-xs font-bold leading-none"
                            :class="idx === currentIndex ? 'text-white' : 'text-gray-400'"
                        >
                            {{ idx + 1 }}
                        </span>
                    </div>
                    <!-- Label + field count -->
                    <div class="flex flex-col items-center gap-0.5">
                        <span
                            v-if="step.label"
                            class="text-[11.5px] whitespace-nowrap transition-colors duration-200 ease-out"
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
                    class="flex-1 relative overflow-hidden h-0.5 mt-[15px] rounded-sm bg-gray-200"
                >
                    <div
                        class="absolute inset-0 bg-gray-900 origin-left transition-transform duration-[400ms] ease-[cubic-bezier(0.4,0,0.2,1)]"
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
