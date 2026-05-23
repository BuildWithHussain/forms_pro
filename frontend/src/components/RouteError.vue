<script setup lang="ts">
import { computed } from "vue";
import { Lock, FileQuestion, AlertTriangle } from "@lucide/vue";
import { Button } from "frappe-ui";
import { useRouter } from "vue-router";

const props = defineProps<{
    excType?: string;
    httpStatus?: number;
    messages?: string[];
}>();

const router = useRouter();

const META: Record<string, { title: string; icon: unknown }> = {
    PermissionError: { title: "Access Denied", icon: Lock },
    DoesNotExistError: { title: "Not Found", icon: FileQuestion },
    AuthenticationError: { title: "Login Required", icon: Lock },
};

const meta = computed(
    () =>
        (props.excType && META[props.excType]) || {
            title: "Something Went Wrong",
            icon: AlertTriangle,
        }
);
const message = computed(() => props.messages?.[0] ?? "");
</script>

<template>
    <div class="flex flex-col items-center justify-center h-full gap-3 p-8 text-center">
        <component :is="meta.icon" class="w-12 h-12 text-ink-gray-5" />
        <h2 class="text-xl font-semibold">{{ meta.title }}</h2>
        <p v-if="message" class="text-sm text-ink-gray-6 max-w-md">{{ message }}</p>
        <p v-if="httpStatus" class="text-xs text-ink-gray-4">HTTP {{ httpStatus }}</p>
        <Button @click="router.replace('/')">Go to Dashboard</Button>
    </div>
</template>
