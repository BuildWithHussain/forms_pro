<template>
    <div class="flex h-screen w-full">
        <Sidebar
            :header="{
                title: sidebarHeader.title,
                subtitle: sidebarHeader.subtitle,
                menuItems: sidebarHeader.menuItems,
            }"
            :sections="sidebarSections"
        >
            <template #header-logo>
                <div
                    class="font-instrument font-bold bg-surface-white rounded border border-outline-gray-1 py-[2px]"
                >
                    F.
                </div>
            </template>
        </Sidebar>
        <slot></slot>
    </div>
</template>
<script setup>
import { session } from "@/data/session";
import { ref, computed } from "vue";
import { Sidebar } from "frappe-ui";
import { LayoutDashboard, ArrowLeftRight, LogOut } from "lucide-vue-next";
import { useUser } from "@/stores/user";

const userStore = useUser();

const props = defineProps({
    sidebarHeader: {
        type: Object,
        default: null,
    },
    sidebarSections: {
        type: Array,
        default: [],
    },
});

const defaultSidebarMenuItems = computed(() => [
    {
        label: "Log out",
        icon: LogOut,
        onClick: session.logout.submit,
    },
]);

const sidebarHeader = computed(() => {
    if (props.sidebarHeader) {
        return props.sidebarHeader;
    }

    return {
        title: "Forms Pro",
        subtitle: session.full_name,
        menuItems: defaultSidebarMenuItems.value,
    };
});

const sidebarSections = computed(() => {
    if (props.sidebarSections && props.sidebarSections.length > 0) {
        return props.sidebarSections;
    }

    const _sections = [
        {
            label: "",
            items: [
                {
                    label: "Dashboard",
                    to: "/",
                    isActive: true,
                    icon: LayoutDashboard,
                },
            ],
        },
    ];

    return _sections;
});
</script>
