<script setup lang="ts">
import { Dialog, ErrorMessage, FileUploader } from "frappe-ui";
import * as z from "zod";
import { reactive, ref, watch } from "vue";
import { useUser } from "@/stores/user";
import TeamLogo from "@/components/team/TeamLogo.vue";
import type { FileType } from "@/components/fields/Attachment.vue";

const user = useUser();
const model = defineModel<boolean>({
    type: Boolean,
    required: true,
});

const formErrors = ref<string>("");

const formSchema = z.object({
    team_name: z
        .string()
        .min(2, "Team name must be at least 2 characters long")
        .max(140, "Team name must be less than 140 characters long"),
    logo_url: z.string().optional(),
});

type Form = z.infer<typeof formSchema>;

const form = reactive<Form>({
    team_name: "",
    logo_url: undefined,
});

watch(
    () => form,
    (newVal) => {
        const result = formSchema.safeParse(newVal);
        if (!result.success) {
            formErrors.value = result.error.issues.map((issue) => issue.message).join(", ");
        } else {
            formErrors.value = "";
        }
    },
    { deep: true }
);

function createTeam() {
    const result = formSchema.safeParse(form);
    if (!result.success) {
        formErrors.value = result.error.issues.map((issue) => issue.message).join(", ");
        return;
    }
    formErrors.value = "";
    user.createTeam(form.team_name, form.logo_url);
    model.value = false;
}

function setTeamLogo(file: FileType) {
    form.logo_url = file.file_url;
}

function removeTeamLogo() {
    form.logo_url = undefined;
}
</script>
<template>
    <Dialog
        v-model="model"
        :options="{
            title: 'Create New Team',
        }"
    >
        <template #body-content>
            <div
                class="flex flex-col items-center gap-4 w-full p-4 rounded bg-surface-gray-1 border border-surface-gray-2"
            >
                <div class="flex flex-col items-center gap-4 my-2">
                    <div class="relative">
                        <Button
                            v-if="form.logo_url"
                            variant="outline"
                            size="sm"
                            class="!text-xs !size-6 absolute -top-2 -right-2 rounded-full"
                            icon="x"
                            @click="removeTeamLogo"
                        />
                        <TeamLogo
                            :team-name="form.team_name"
                            class="size-12"
                            :logo-url="form.logo_url ?? null"
                        />
                    </div>
                    <div class="text-xs text-ink-gray-6 text-center flex flex-col gap-2">
                        <p>The team logo is automatically generated based on the team name.</p>
                        <div class="flex gap-2 items-center justify-center">
                            <p>Don't like it?</p>
                            <FileUploader
                                @success="(file: FileType) => setTeamLogo(file)"
                                :fileTypes="['image/png', 'image/jpeg', 'image/jpg', 'image/gif']"
                            >
                                <!-- @vue-ignore -->
                                <template
                                    #default="{
                                        file,
                                        uploading,
                                        progress,
                                        uploaded,
                                        message,
                                        error,
                                        total,
                                        success,
                                        openFileSelector,
                                    }"
                                >
                                    <ErrorMessage :message="error" />
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        class="!text-xs"
                                        @click="openFileSelector"
                                        :loading="uploading"
                                    >
                                        Upload your own
                                    </Button>
                                </template>
                            </FileUploader>
                        </div>
                    </div>
                </div>
                <input
                    type="text"
                    v-model="form.team_name"
                    class="text-lg text-ink-gray-9 !outline-0 !ring-0 !border-0 bg-inherit text-center"
                    placeholder="Enter team name"
                />
                <ErrorMessage :message="formErrors" />
                <Button
                    @click="createTeam"
                    class="w-full"
                    variant="outline"
                    :disabled="formErrors !== ''"
                >
                    Create Team
                </Button>
            </div>
        </template>
    </Dialog>
</template>
