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
                        :options="doctypesList.data"
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
                            handleCreateDraftFormWithDoctype();
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
            <template v-if="user.user?.has_desk_access">
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
            </template>
            <template v-else>
                <Button
                    class="w-fit"
                    variant="solid"
                    iconLeft="plus"
                    @click="handleCreateDraftForm"
                >
                    Create New
                </Button>
            </template>
            <div class="flex flex-col gap-2">
                <h3 class="font-medium">Recent</h3>
                <p class="text-sm" v-if="teamForms.loading">Loading...</p>
                <p class="text-sm" v-else-if="!teamForms.data || teamForms.data.length === 0">
                    No forms created yet
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" v-else>
                    <div v-for="form in teamForms.data" :key="form.name">
                        <FormPreviewCard :form="form" />
                    </div>
                </div>
            </div>
        </div>
    </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from "@/layouts/BaseLayout.vue";
import { useRouter } from "vue-router";
import { onMounted, ref, watch } from "vue";
import { toast } from "vue-sonner";
import { useUser } from "@/stores/user";
import { Dropdown, Dialog, createResource, Combobox } from "frappe-ui";
import { createNewFormWithDoctype, createNewForm } from "@/utils/form_generator";
import FormPreviewCard from "@/components/dashboard/FormPreviewCard.vue";
const router = useRouter();
const showSelectDoctypeDialog = ref(false);
const selectedDoctype = ref<string | null>(null);

const user = useUser();

const doctypesList = createResource({
    url: "forms_pro.api.form.get_doctype_list",
});

const handleCreateDraftFormWithDoctype = async () => {
    if (!selectedDoctype.value || !user.currentTeam?.name) {
        toast.error("Error occured while creating form. Check DocType Selected.");
        return;
    }
    const data = await createNewFormWithDoctype(selectedDoctype.value, user.currentTeam.name);
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};

const handleCreateDraftForm = async () => {
    if (!user.currentTeam?.name) {
        toast.error("Error occured while creating form. User has no default team.");
        return;
    }
    const data = await createNewForm(user.currentTeam.name);
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};

const teamForms = createResource({
    url: "forms_pro.api.team.get_team_forms",
    makeParams() {
        return {
            team_id: user.currentTeam?.name,
        };
    },
    loading: true,
    cache: "teamForms",
});

watch(
    () => user.currentTeam,
    (currentTeam) => {
        if (currentTeam) {
            teamForms.fetch();
        }
    },
    { immediate: true }
);

watch(
    user.user,
    (user) => {
        if (user?.has_desk_access) {
            doctypesList.fetch();
        }
    },
    { immediate: true }
);
</script>
