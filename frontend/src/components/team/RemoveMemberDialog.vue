<script setup lang="ts">
import { Dialog } from "frappe-ui";
import { useTeam } from "@/stores/team";
import type { TeamMember } from "@/stores/team";

const teamStore = useTeam();
const open = defineModel<boolean>({ required: true, default: false });
const memberEmail = defineModel<TeamMember>("memberEmail", { required: true });

function removeMember() {
    teamStore.removeMemberFromTeam(memberEmail.value.email);
    open.value = false;
}
</script>
<template>
    <Dialog
        v-model="open"
        :options="{
            title: 'Confirm Removal',
            icon: {
                name: 'alert-triangle',
                appearance: 'warning',
            },
            actions: [
                {
                    label: 'Remove',
                    theme: 'red',
                    onClick: () => {
                        removeMember();
                    },
                },
                {
                    label: 'Cancel',
                    onClick: () => {
                        open = false;
                    },
                },
            ],
        }"
    >
        <template #body-content>
            <div class="text-p-base">
                Are you sure you want to remove
                <strong>{{ memberEmail.full_name }}</strong> from the team?
            </div>
        </template>
    </Dialog>
</template>
