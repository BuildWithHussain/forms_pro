<script setup lang="ts">
import { Dialog } from "frappe-ui";
import { useManageForm } from "@/stores/form/manageForm";

const manageFormStore = useManageForm();

const open = defineModel<boolean>({ required: true, default: false });
const selectedUserToRemove = defineModel<string | null>("selectedUserToRemove", {
    required: true,
    default: null,
});

function removeAccess() {
    manageFormStore.removeAccess(selectedUserToRemove.value);
}
</script>
<template>
    <Dialog
        v-model="open"
        :options="{
            title: 'Confirm Removal',
            message: `Are you sure you want to remove access for ${selectedUserToRemove}?`,
            icon: {
                name: 'alert-triangle',
                appearance: 'warning',
            },
            actions: [
                {
                    label: 'Remove',
                    theme: 'red',
                    onClick: () => {
                        removeAccess();
                        open = false;
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
    ></Dialog>
</template>
