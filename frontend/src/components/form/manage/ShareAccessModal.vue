<script setup lang="ts">
import { Button, Dialog, MultiSelect } from "frappe-ui";
import { useTeam, type TeamMember } from "@/stores/team";
import { useManageForm, type SharedAccessUser } from "@/stores/form/manageForm";
import { computed, ref } from "vue";
import Avatar from "@/components/ui/Avatar.vue";
import { toast } from "vue-sonner";

const teamStore = useTeam();
teamStore.initialize();
const manageFormStore = useManageForm();

const open = defineModel<boolean>({ required: true, default: false });

const sharedAccessUsers = computed(() => manageFormStore.sharedAccessUsers);

const teamMembersNotSharedWith = computed(() => {
    return teamStore.teamMembers.filter((member: TeamMember) => {
        return !sharedAccessUsers.value.some(
            (user: SharedAccessUser) => user.email === member.email
        );
    });
});

const multiSelectOptions = computed(() => {
    return teamMembersNotSharedWith.value.map((member: TeamMember) => {
        return {
            label: member.full_name,
            value: member.email,
        };
    });
});

const selectedUsers = ref<string[]>([]);

const giveAccessToUsers = () => {
    selectedUsers.value.forEach((user) => {
        manageFormStore.addAccess(user, {
            read: true,
            write: true,
            share: true,
            submit: false,
        });
    });
    toast.success("Access given to users successfully");
    selectedUsers.value = [];
};

const giveAccessToAllTeamMembers = () => {
    teamMembersNotSharedWith.value.forEach((member: TeamMember) => {
        manageFormStore.addAccess(member.email, {
            read: true,
            write: true,
            share: true,
            submit: false,
        });
    });
    toast.success("Access given to all team members successfully");
    selectedUsers.value = [];
};
</script>
<template>
    <Dialog
        v-model="open"
        :options="{
            title: 'Share Access',
            actions: [
                {
                    label: 'Share Access',
                    disabled: selectedUsers.length === 0,
                    onClick: () => {
                        giveAccessToUsers();
                        open = false;
                    },
                    variant: 'solid',
                },
            ],
        }"
    >
        <template #body-content>
            <div class="flex flex-col gap-2">
                <p class="text-ink-gray-6 text-base">
                    Add users from your team to give access to this form
                </p>
                <Button
                    class="w-fit"
                    variant="outline"
                    size="sm"
                    icon-left="plus"
                    @click="
                        () => {
                            giveAccessToAllTeamMembers();
                            open = false;
                        }
                    "
                >
                    Give Access to All Team Members
                </Button>
                <MultiSelect :options="multiSelectOptions" v-model="selectedUsers">
                    <template #option="{ item }">
                        <Avatar :userId="item.value" size="sm" />
                        <span class="text-ink-gray-8 text-sm ml-2">{{ item.label }}</span>
                    </template>
                </MultiSelect>
            </div>
        </template>
    </Dialog>
</template>
