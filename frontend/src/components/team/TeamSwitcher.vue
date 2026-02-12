<script setup lang="ts">
import { useUser } from "@/stores/user";
import { Dropdown } from "frappe-ui";
import { ChevronsUpDown } from "lucide-vue-next";
import { computed, inject, ref } from "vue";
import CreateTeamDialog from "@/components/team/CreateTeamDialog.vue";
import TeamSwitcherItem from "@/components/team/TeamSwitcherItem.vue";
import TeamLogo from "@/components/team/TeamLogo.vue";

const isSidebarCollapsed = inject("isSidebarCollapsed");

const showCreateTeamDialog = ref(false);
const userStore = useUser();

const teamOptions = computed(() => {
    return userStore.userTeams
        ?.filter((team) => team.name !== userStore.currentTeam?.name)
        .map((team) => ({
            label: `${team.team_name}`,
            logoUrl: team.logo ?? undefined,
            isTeam: true,
            onClick: () => {
                userStore.switchTeam(team);
            },
        }));
});

const groupOptions = computed(() => {
    return [
        {
            group: "Switch Team",
            items: teamOptions.value,
        },
        {
            group: "",
            items: [
                {
                    label: "Create New Team",
                    onClick: () => {
                        showCreateTeamDialog.value = true;
                    },
                    icon: "plus",
                },
            ],
        },
    ];
});
</script>
<template>
    <CreateTeamDialog v-model="showCreateTeamDialog" />
    <Dropdown :options="groupOptions">
        <template #default="{ open }">
            <div
                class="flex items-center gap-2 p-2 rounded cursor-pointer transition-colors duration-150 ease-[cubic-bezier(0.4, 0, 0.2, 1)] hover:bg-surface-gray-2"
                :class="{ 'bg-surface-white': open, 'px-1.5 ': isSidebarCollapsed }"
            >
                <TeamLogo
                    v-if="isSidebarCollapsed"
                    :team-name="userStore.currentTeam!.team_name"
                    :logo-url="userStore.currentTeam?.logo ?? null"
                />
                <div v-else class="flex items-center gap-2 justify-between w-full">
                    <TeamSwitcherItem
                        :label="userStore.currentTeam!.team_name"
                        :logo-url="userStore.currentTeam?.logo ?? null"
                    />
                    <ChevronsUpDown class="size-4 text-ink-gray-6" />
                </div>
            </div>
        </template>
        <template #item="{ item }">
            <!-- @vue-expect-error -->
            <TeamSwitcherItem
                v-if="item.isTeam"
                class="p-2 w-full hover:bg-surface-gray-2 cursor-pointer rounded"
                :label="item.label"
                :logo-url="item.logoUrl"
            />
            <Button
                v-else
                variant="ghost"
                @click="item.onClick"
                :icon-left="item.icon"
                class="w-full"
                :label="item.label"
            />
        </template>
    </Dropdown>
</template>
