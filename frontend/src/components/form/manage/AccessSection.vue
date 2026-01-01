<script setup lang="ts">
import { useManageForm } from "@/stores/form/manageForm";
import { ref } from "vue";
import { Button, Checkbox, ListView } from "frappe-ui";
import Avatar from "@/components/ui/Avatar.vue";
import type { PermissionTypes } from "@/stores/form/manageForm";
import ShareAccessModal from "./ShareAccessModal.vue";
import RemoveAccessModal from "./RemoveAccessModal.vue";

const manageFormStore = useManageForm();
const openModal = ref(false);
const openRemoveAccessModal = ref(false);
const selectedUserToRemove = ref<string | null>(null);

function showRemoveAccessModal(email: string) {
    selectedUserToRemove.value = email;
    openRemoveAccessModal.value = true;
}

const columns = ref([
    {
        label: "Name",
        key: "full_name",
        width: 2,
    },
    {
        label: "",
        key: "comment",
    },
    {
        label: "Read",
        key: "read",
    },
    {
        label: "Write",
        key: "write",
    },
    {
        label: "Share",
        key: "share",
    },
    {
        label: "Actions",
        key: "actions",
    },
]);

function setPermission(row: any, column: any, value: boolean) {
    const userId = row.email;
    const permission = column.key as PermissionTypes;
    manageFormStore.setPermission(userId, permission, value);
}
</script>
<template>
    <ShareAccessModal v-model="openModal" />
    <RemoveAccessModal
        v-model="openRemoveAccessModal"
        v-model:selected-user-to-remove="selectedUserToRemove"
    />
    <div class="flex flex-col gap-4">
        <div class="space-y-1">
            <p class="text-base font-medium text-ink-gray-8">Manage access to this form</p>
            <p class="text-sm text-ink-gray-5">
                You can add or remove access to the form for each user of your team.
            </p>
        </div>
        <div class="flex gap-2">
            <Button variant="outline" size="sm" icon-left="plus" @click="openModal = true">
                Share Access
            </Button>
        </div>
        <ListView
            :columns="columns"
            :rows="manageFormStore.formAccessResource.data"
            :options="{
                selectable: false,
            }"
            row-key="email"
        >
            <template #cell="{ item, row, column }">
                <div
                    v-if="column.key === 'full_name'"
                    class="flex items-center gap-2 text-ink-gray-8 text-sm"
                >
                    <Avatar :userId="row.email" />
                    <p>{{ row.full_name }}</p>
                </div>
                <div v-else-if="column.key === 'comment'" class="flex">
                    <span
                        v-if="row.email === manageFormStore.formOwner"
                        class="text-ink-gray-5 text-sm italic"
                    >
                        Owner
                    </span>
                </div>
                <div v-else-if="column.key === 'actions'" class="flex">
                    <Button
                        size="sm"
                        theme="red"
                        icon="trash"
                        @click="showRemoveAccessModal(row.email)"
                        :disabled="row.email === manageFormStore.formOwner"
                        :tooltip="
                            row.email === manageFormStore.formOwner
                                ? 'Owner cannot be removed'
                                : 'Remove Access'
                        "
                    />
                </div>
                <div v-else class="flex">
                    <Checkbox
                        :disabled="
                            !manageFormStore.userHasShareAccess ||
                            row.email === manageFormStore.formOwner
                        "
                        :model-value="item"
                        @update:model-value="setPermission(row, column, $event)"
                    />
                </div>
            </template>
        </ListView>
    </div>
</template>
