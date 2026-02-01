<script setup lang="ts">
import { Avatar as FrappeAvatar, Tooltip } from "frappe-ui";
import { getUser } from "@/utils/user";
import type { GetUserBasicResponse } from "@/utils/user";
import { ref, onMounted } from "vue";

const props = withDefaults(
    defineProps<{
        userId: string;
        size?: "xs" | "sm" | "md" | "lg" | "xl" | "2xl" | "3xl";
        variant?: "default" | "outline" | "filled";
        shape?: "circle" | "square";
        className?: string;
        disabled?: boolean;
    }>(),
    {
        size: "md",
        variant: "default",
        shape: "circle",
        disabled: false,
    }
);

const user = ref<GetUserBasicResponse | null>(null);

onMounted(async () => {
    if (props.userId) {
        user.value = await getUser(props.userId);
    }
});
</script>

<template>
    <Tooltip
        v-if="user?.full_name"
        :disabled="disabled"
        :text="user?.full_name"
        placement="bottom"
    >
        <FrappeAvatar
            :size="size"
            :shape="shape"
            :image="user?.user_image ?? undefined"
            :label="user?.full_name"
        />
    </Tooltip>
</template>
