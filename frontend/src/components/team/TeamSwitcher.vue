<script setup lang="ts">
import { useUser } from "@/stores/user";
import { Dropdown, TextInput } from "frappe-ui";
import { ChevronsUpDown, Search } from "lucide-vue-next";
import { computed, inject, ref } from "vue";
import CreateTeamDialog from "@/components/team/CreateTeamDialog.vue";
import TeamSwitcherItem from "@/components/team/TeamSwitcherItem.vue";
import TeamLogo from "@/components/team/TeamLogo.vue";

type TeamSwitcherOption = {
    label: string;
    isSearch?: boolean;
    isTeam?: boolean;
    logoUrl?: string;
    icon?: string;
    onClick?: (e?: Event) => void;
};

const isSidebarCollapsed = inject("isSidebarCollapsed");

const showCreateTeamDialog = ref(false);
const searchQuery = ref("");
const userStore = useUser();

const teamOptions = computed(() => {
    const teams =
        userStore.userTeams?.filter(
            (team) =>
                team.name !== userStore.currentTeam?.name &&
                team.team_name.toLowerCase().includes(searchQuery.value.trim().toLowerCase())
        ) ?? [];
    return teams.map((team) => ({
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
            group: "",
            hideLabel: true,
            items: [
                {
                    label: "Search",
                    isSearch: true,
                    onClick: (e: Event) => e?.preventDefault?.(),
                },
            ],
        },
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
    <!-- Width matches sidebar (sidebar is w-60 when expanded, w-12 when collapsed) -->
    <div class="w-full min-w-0">
        <Dropdown v-if="userStore.currentTeam" :options="groupOptions">
            <template #default="{ open }">
                <div
                    class="flex items-center gap-2 p-2 rounded cursor-pointer transition-colors duration-150 ease-[cubic-bezier(0.4, 0, 0.2, 1)] hover:bg-surface-gray-2 w-full min-w-0"
                    :class="{ 'bg-surface-white': open, 'px-1.5 ': isSidebarCollapsed }"
                >
                    <TeamLogo
                        v-if="isSidebarCollapsed"
                        :team-name="userStore.currentTeam?.team_name"
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
                <div v-if="(item as TeamSwitcherOption).isSearch" class="p-2" @click.stop>
                    <TextInput
                        v-model="searchQuery"
                        placeholder="Search Team"
                        size="sm"
                        variant="subtle"
                        class="w-full"
                    >
                        <template #prefix>
                            <Search class="size-4 text-ink-gray-5" />
                        </template>
                    </TextInput>
                </div>
                <TeamSwitcherItem
                    v-else-if="(item as TeamSwitcherOption).isTeam"
                    class="p-2 w-full hover:bg-surface-gray-2 cursor-pointer rounded"
                    :label="item.label"
                    :logo-url="(item as TeamSwitcherOption).logoUrl ?? null"
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
    </div>
</template>
