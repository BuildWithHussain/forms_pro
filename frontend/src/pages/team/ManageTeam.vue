<script setup lang="ts">
import { useTeam } from "@/stores/team";
import TeamMemberList from "@/components/team/TeamMemberList.vue";
import { Breadcrumbs, LoadingText } from "frappe-ui";
import ManageTeamHeader from "@/components/team/ManageTeamHeader.vue";
import RouteError from "@/components/RouteError.vue";
import { useRouteData } from "@/composables/useRouteData";

const teamStore = useTeam();
teamStore.initialize();
const { status, error } = useRouteData();
</script>
<template>
    <RouteError
        v-if="status === 'error'"
        :exc-type="error?.excType"
        :http-status="error?.httpStatus"
        :messages="error?.messages"
    />
    <div v-else-if="teamStore.teamMembersResource.loading">
        <LoadingText text="Loading team info..." class="h-5" />
    </div>
    <div v-else>
        <div class="flex flex-col gap-8">
            <div class="flex flex-col gap-2">
                <Breadcrumbs :items="[{ label: 'Team', route: '/team' }, { label: 'Manage' }]" />
                <h2 class="text-3xl font-bold">Manage Team</h2>
                <p class="text-base">Manage your team and its members</p>
            </div>
            <ManageTeamHeader />
            <div class="flex flex-col gap-2">
                <TeamMemberList />
            </div>
        </div>
    </div>
</template>
