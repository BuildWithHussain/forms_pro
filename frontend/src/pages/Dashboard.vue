<template>
    <BaseLayout>
        <Dialog
            v-model="showSelectDoctypeDialog"
            :options="{
                title: 'Select DocType',
            }"
        >
            <template #body-content>
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">DocType</label>
                    <Combobox
                        v-model="selectedDoctype"
                        :options="doctypes.data"
                        label="DocType"
                        id="doctype"
                    />
                </div>
            </template>
            <template #actions="{ close }">
                <Button
                    class="w-full"
                    variant="solid"
                    :disabled="!selectedDoctype"
                    @click="
                        () => {
                            handleCreateDraftFormWithDoctype(selectedDoctype.value);
                        }
                    "
                    >Create</Button
                >
            </template>
        </Dialog>
        <div class="p-4 flex flex-col gap-4 w-full overflow-y-auto">
            <div class="flex flex-col gap-2">
                <h2 class="text-3xl font-bold">Dashboard</h2>
                <p class="text-base">Manage and create forms</p>
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
                            showSelectDoctypeDialog = true;
                        },
                    },
                ]"
            />
            <div class="flex flex-col gap-2">
                <h3 class="font-medium">Recents</h3>
                <p class="text-sm text-gray-500" v-if="userForms.loading">Loading...</p>
                <p class="text-sm text-gray-500" v-else-if="userForms.data?.length === 0">
                    No forms created yet
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" v-else>
                    <div v-for="form in userForms.data" :key="form.name">
                        <FormPreviewCard :form="form" />
                    </div>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script setup>
import BaseLayout from "@/layouts/BaseLayout.vue";
import { useRouter } from "vue-router";
import { ref } from "vue";
import {
    Dropdown,
    Dialog,
    FormControl,
    createListResource,
    Card,
    createResource,
    Combobox,
} from "frappe-ui";
import { session } from "@/data/session";
import { createNewFormWithDoctype, createNewForm } from "@/utils/form_generator";
import FormPreviewCard from "@/components/dashboard/FormPreviewCard.vue";
const router = useRouter();
const showSelectDoctypeDialog = ref(false);

const handleCreateDraftFormWithDoctype = async () => {
    const data = await createNewFormWithDoctype(selectedDoctype.value);
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};

const handleCreateDraftForm = async () => {
    const data = await createNewForm();
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};

const userForms = createListResource({
    doctype: "Form",
    filters: {
        owner: session.user,
    },
    fields: ["name", "title", "creation", "modified", "is_published", "route"],
    orderBy: "modified desc",
    auto: true,
    pageLength: 9999,
});

const doctypes = createResource({
    url: "forms_pro.api.form.get_doctype_list",
    auto: true,
});
const selectedDoctype = ref(null);
</script>
