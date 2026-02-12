<template>
    <div class="flex h-screen w-full">
        <Sidebar :sections="sidebarSections">
            <template #header>
                <TeamSwitcher />
            </template>
            <template #footer-items="{ isCollapsed }">
                <Popover placement="top-start">
                    <template #target="{ togglePopover, isOpen }">
                        <div
                            @click="togglePopover"
                            class="p-2 z-10 rounded-md flex gap-2 items-center hover:bg-surface-white cursor-pointer duration-200 ease-[cubic-bezier(0.4, 0, 0.2, 1)]"
                            :class="{ 'bg-surface-white': isOpen, '!p-1': isCollapsed }"
                        >
                            <Avatar
                                :disabled="true"
                                v-if="session.user"
                                :user-id="session.user"
                                size="lg"
                                shape="square"
                            />
                            <div v-if="!isCollapsed" class="flex items-center gap-2">
                                <div class="flex flex-col gap-1">
                                    <span class="text-base font-medium text-ink-gray-7">
                                        {{ session.full_name }}
                                    </span>
                                    <span class="text-xs text-ink-gray-5">{{ session.user }}</span>
                                </div>
                                <EllipsisVertical class="size-4 text-ink-gray-6" />
                            </div>
                        </div>
                    </template>
                    <template #body>
                        <div
                            class="flex flex-col gap-2 bg-surface-white shadow-2xl z-0 rounded-t-lg -mb-2 p-2 pb-4 w-full"
                            :class="{ 'rounded-br-lg': isCollapsed }"
                        >
                            <Button
                                variant="ghost"
                                theme="red"
                                @click="session.logout.submit"
                                label="Log out"
                                icon-left="log-out"
                            />
                        </div>
                    </template>
                </Popover>
            </template>
        </Sidebar>
        <slot> </slot>
    </div>
</template>
<script setup lang="ts">
import { session } from "@/data/session";
import { computed } from "vue";
import { Popover, Sidebar, type SidebarProps } from "frappe-ui";
import { EllipsisVertical, LayoutDashboard } from "lucide-vue-next";
import type { PropType } from "vue";
import Avatar from "@/components/ui/Avatar.vue";
import TeamSwitcher from "@/components/team/TeamSwitcher.vue";

type SidebarSectionProps = NonNullable<SidebarProps["sections"]> extends (infer T)[] ? T : never;
type SidebarHeaderProps = NonNullable<SidebarProps["header"]>;

const props = defineProps({
    sidebarHeader: {
        type: Object as PropType<SidebarHeaderProps | null>,
        default: null,
    },
    sidebarSections: {
        type: Array as PropType<SidebarSectionProps[]>,
        default: () => [],
    },
});

const sidebarSections = computed((): SidebarSectionProps[] => {
    if (props.sidebarSections && props.sidebarSections.length > 0) {
        return props.sidebarSections;
    }

    const _sections: SidebarSectionProps[] = [
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
