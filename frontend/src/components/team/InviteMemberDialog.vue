<script setup lang="ts">
import { ref } from "vue";
import * as z from "zod";
import {
    Dialog,
    FormControl,
    ErrorMessage,
    Button,
    Avatar as FrappeAvatar,
    useCall,
} from "frappe-ui";
import { useTeam } from "@/stores/team";
import { toast } from "vue-sonner";

const team = useTeam();

const inviteEmails = ref<string[]>([]);
const emailInput = ref("");
const emailInputError = ref<string>("");

const emailSchema = z.email();

function addInviteEmail() {
    const trimmed = emailInput.value.trim();
    if (!trimmed) return;
    const result = emailSchema.safeParse(trimmed);
    if (!result.success) {
        emailInputError.value = result.error.issues.map((issue) => issue.message).join(", ");
        return;
    }
    if (inviteEmails.value.includes(result.data)) {
        emailInputError.value = "Email already added";
        return;
    }
    inviteEmails.value.push(result.data);
    emailInput.value = "";
    emailInputError.value = "";
}

function removeInviteEmail(email: string) {
    inviteEmails.value = inviteEmails.value.filter((e) => e !== email);
}

function sendInvitationEmails() {
    useCall({
        baseUrl: "/api/v2/method/",
        url: "forms_pro.api.team.invite_team_members",
        method: "POST",
        params: {
            team_id: team.currentTeam?.name,
            emails: inviteEmails.value,
        },
        onSuccess: () => {
            toast.success("Invitations sent successfully");
            open.value = false;
            inviteEmails.value = [];
        },
        onError: (error: Error) => {
            toast.error("Failed to send invitations", {
                description: error.message,
            });
        },
    });
}

const open = defineModel<boolean>({ required: true, default: false });
</script>
<template>
    <Dialog
        v-model="open"
        :options="{
            title: 'Invite members to your team',
            size: 'lg',
            actions: [
                {
                    label: 'Send Invitations',
                    disabled: inviteEmails.length === 0,
                    variant: 'solid',
                    iconLeft: 'send',
                    onClick: () => {
                        sendInvitationEmails();
                    },
                },
            ],
        }"
    >
        <template #body-content>
            <div class="flex flex-col gap-4">
                <div class="flex items-center gap-2">
                    <FormControl
                        v-model="emailInput"
                        label="Invite by Email"
                        type="email"
                        variant="outline"
                        class="flex-1"
                        @keydown.enter.prevent="addInviteEmail"
                        description="Enter email and press Enter"
                    />
                    <Button size="sm" icon-left="plus" @click="addInviteEmail"> Add </Button>
                </div>
                <ErrorMessage :message="emailInputError" />
                <ul v-if="inviteEmails.length" class="flex flex-col gap-2">
                    <span class="text-base font-medium text-ink-gray-8">Recipients</span>
                    <li v-for="email in inviteEmails" :key="email" class="flex items-center gap-2">
                        <FrappeAvatar :label="email" size="sm" />
                        <span class="text-sm text-ink-gray-6 flex-1">{{ email }}</span>
                        <Button
                            icon="trash"
                            variant="subtle"
                            size="sm"
                            @click="removeInviteEmail(email)"
                        />
                    </li>
                </ul>
            </div>
        </template>
    </Dialog>
</template>
