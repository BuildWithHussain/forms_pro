<template>
    <div class="flex h-screen w-full">
        <Sidebar
            :header="{
                title: 'Forms Pro',
                subtitle: session.full_name,
                menuItems: menuItems,
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
import toggleTheme from "@/utils/theme";
import { useUser } from "@/stores/user";
const userStore = useUser();

const menuItems = computed(() => {
    return [
        // {
        //     label: "Switch Teams",
        //     icon: ArrowLeftRight,
        //     onClick: () => {
        //         console.log("Switch Teams");
        //     },
        // },
        {
            label: "Log out",
            icon: LogOut,
            onClick: session.logout.submit,
        },
    ];
});

const sidebarSections = ref([
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
    // {
    // 	label: "",
    // 	items: [
    // 		{
    // 			label: "Submissions",
    // 			to: "/submissions",
    // 		},
    // 	],
    // },
]);
</script>
