<template>
    <nav class="bg-white border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
            <div class="flex flex-col gap-1">
                <h1 class="text-4xl font-bold text-gray-900">Dashboard</h1>
                <p class="text-base text-gray-600">Manage and create forms</p>
            </div>
            <Dropdown
                class="w-fit"
                :button="{
                    label: 'Create',
                    iconLeft: 'plus',
                    variant: 'solid',
                }"
                :options="[
                    {
                        label: 'Create New',
                        onClick: handleCreateDraftForm,
                    },
                    {
                        label: 'Create from Existing DocType',
                        onClick: () => {
                            emit('show-doctype-dialog');
                        },
                    },
                ]"
            />
        </div>
    </nav>
</template>

<script setup>
import { Dropdown } from "frappe-ui";
import { useRouter } from "vue-router";
import { createNewForm } from "@/utils/form_generator";

const router = useRouter();
const emit = defineEmits(["show-doctype-dialog"]);

const handleCreateDraftForm = async () => {
    const data = await createNewForm();
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};
</script>

