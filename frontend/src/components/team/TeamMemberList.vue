<script setup lang="ts">
import { computed, ref } from "vue";
import { useTeam, type TeamMember } from "@/stores/team";
import { ListView, Checkbox, Tooltip, Button } from "frappe-ui";
import Avatar from "@/components/ui/Avatar.vue";
import InviteMemberDialog from "./InviteMemberDialog.vue";
import RemoveMemberDialog from "./RemoveMemberDialog.vue";

const teamStore = useTeam();
const openInviteMemberDialog = ref<boolean>(false);
const openRemoveMemberDialog = ref<boolean>(false);
const memberToRemove = ref<TeamMember | null>(null);

const columns = computed(() => [
    {
        label: "Name",
        key: "full_name",
        width: 3,
    },
    {
        label: "Can Add Members?",
        key: "can_edit_team",
        width: 3,
    },
    {
        label: "Actions",
        key: "actions",
        width: 1,
    },
]);

function handleMemberRemoval(row: TeamMember) {
    memberToRemove.value = row;
    openRemoveMemberDialog.value = true;
}
</script>
<template>
    <InviteMemberDialog v-model="openInviteMemberDialog" />
    <RemoveMemberDialog v-model="openRemoveMemberDialog" v-model:member="memberToRemove" />
    <div class="flex flex-col gap-2">
        <div class="flex justify-between items-center">
            <h3 class="font-medium">Team Members</h3>
            <Button
                icon-left="plus"
                label="Invite Member"
                variant="outline"
                @click="openInviteMemberDialog = true"
            />
        </div>
        <ListView
            :selectable="false"
            :columns="columns"
            :rows="teamStore.teamMembers"
            :options="{
                selectable: false,
                emptyState: {
                    title: 'No Team Members Added',
                    description: 'Add team members to your team to get started',
                },
            }"
            row-key="email"
        >
            <!-- @vue-expect-error -->
            <template #cell="{ item, row, column }">
                <Checkbox
                    v-if="column.key === 'can_edit_team'"
                    :disabled="row.is_owner"
                    :model-value="row.can_edit_team"
                    @update:model-value="
                        () => {
                            teamStore.toggleEditPermissionForMember(row.email);
                        }
                    "
                />
                <div v-else-if="column.key === 'actions'">
                    <Tooltip v-if="row.is_owner" text="Owner cannot be removed from the team">
                        <span class="text-sm text-ink-gray-5 italic">Owner</span>
                    </Tooltip>
                    <Button
                        v-else
                        size="sm"
                        variant="ghost"
                        icon="trash"
                        :label="`Remove ${row.full_name} from the team`"
                        @click="handleMemberRemoval(row)"
                    />
                </div>
                <div class="flex items-center gap-2" v-else>
                    <Avatar :userId="row.email" />
                    <span class="text-base">{{ row.full_name }}</span>
                </div>
            </template>
        </ListView>
    </div>
</template>
