<script setup lang="ts">
import { computed, watch, onUnmounted, useSlots } from "vue";
import { Button } from "frappe-ui";

export interface DrawerAction {
    label: string;
    variant?: "solid" | "outline" | "ghost" | "subtle";
    theme?: "gray" | "blue" | "green" | "red";
    onClick?: (close: () => void) => void;
    disabled?: boolean;
    loading?: boolean;
}

const props = withDefaults(
    defineProps<{
        size?: "sm" | "md" | "lg";
        position?: "top" | "bottom" | "right" | "left";
        title?: string | null;
        actions?: DrawerAction[] | null;
    }>(),
    {
        size: "md",
        position: "right",
        title: null,
        actions: null,
    }
);

const slots = useSlots();
const open = defineModel<boolean>({ default: false });

function close() {
    open.value = false;
}

function onKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") close();
}

watch(open, (isOpen) => {
    if (isOpen) {
        document.addEventListener("keydown", onKeydown);
        document.body.style.overflow = "hidden";
    } else {
        document.removeEventListener("keydown", onKeydown);
        document.body.style.overflow = "";
    }
});

onUnmounted(() => {
    document.removeEventListener("keydown", onKeydown);
    document.body.style.overflow = "";
});

const showActions = computed(() => {
    return (props.actions && props.actions.length > 0) || !!slots.actions;
});

const panelClasses = computed(() => {
    const isHorizontal = props.position === "left" || props.position === "right";

    const sizeClasses = {
        horizontal: { sm: "w-80", md: "w-[26rem]", lg: "w-[35rem]" },
        vertical: { sm: "h-[30vh]", md: "h-[50vh]", lg: "h-[70vh]" },
    };

    const orientation = isHorizontal ? "horizontal" : "vertical";
    const dimension = sizeClasses[orientation][props.size];

    const positionClasses = {
        right: `top-0 right-0 h-full ${dimension} max-w-[90vw]`,
        left: `top-0 left-0 h-full ${dimension} max-w-[90vw]`,
        top: `top-0 left-0 w-full ${dimension} max-h-[90vh]`,
        bottom: `bottom-0 left-0 w-full ${dimension} max-h-[90vh]`,
    };

    return positionClasses[props.position];
});

const transitionName = computed(() => `drawer-${props.position}`);
</script>

<template>
    <Teleport to="body">
        <Transition name="drawer-overlay" appear>
            <div
                v-if="open"
                class="fixed inset-0 z-50 bg-black/30 dark:bg-black/50"
                @click="close"
            />
        </Transition>

        <Transition :name="transitionName" appear>
            <div
                v-if="open"
                role="dialog"
                aria-modal="true"
                :class="panelClasses"
                class="fixed z-50 flex flex-col bg-surface-modal shadow-2xl"
            >
                <!-- Title -->
                <div
                    class="flex items-center justify-between shrink-0 px-5 py-3.5"
                    :class="{
                        'border-b border-surface-gray-2': title || $slots.title,
                    }"
                >
                    <slot name="title">
                        <h3
                            v-if="title"
                            class="text-lg font-semibold text-ink-gray-9 truncate pr-2"
                        >
                            {{ title }}
                        </h3>
                    </slot>
                    <Button
                        variant="ghost"
                        icon="x"
                        size="sm"
                        class="ml-auto shrink-0"
                        @click="close"
                    />
                </div>

                <!-- Body -->
                <div class="flex-1 overflow-y-auto px-5 py-4">
                    <slot />
                </div>

                <!-- Actions -->
                <div
                    v-if="showActions"
                    class="shrink-0 border-t border-surface-gray-2 px-5 py-3.5"
                >
                    <slot name="actions" :close="close">
                        <div class="flex items-center justify-end gap-2">
                            <Button
                                v-for="(action, index) in actions"
                                :key="index"
                                :variant="action.variant ?? 'outline'"
                                :theme="action.theme"
                                :disabled="action.disabled"
                                :loading="action.loading"
                                @click="action.onClick?.(close)"
                            >
                                {{ action.label }}
                            </Button>
                        </div>
                    </slot>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.drawer-overlay-enter-active {
    transition: opacity 0.3s ease;
}
.drawer-overlay-leave-active {
    transition: opacity 0.2s ease;
}
.drawer-overlay-enter-from,
.drawer-overlay-leave-to {
    opacity: 0;
}

.drawer-right-enter-active,
.drawer-left-enter-active,
.drawer-top-enter-active,
.drawer-bottom-enter-active {
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-right-leave-active,
.drawer-left-leave-active,
.drawer-top-leave-active,
.drawer-bottom-leave-active {
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-right-enter-from,
.drawer-right-leave-to {
    transform: translateX(100%);
}

.drawer-left-enter-from,
.drawer-left-leave-to {
    transform: translateX(-100%);
}

.drawer-top-enter-from,
.drawer-top-leave-to {
    transform: translateY(-100%);
}

.drawer-bottom-enter-from,
.drawer-bottom-leave-to {
    transform: translateY(100%);
}
</style>
