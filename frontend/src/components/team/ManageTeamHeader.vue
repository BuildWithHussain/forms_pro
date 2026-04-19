<script setup lang="ts">
import TeamLogo from "@/components/team/TeamLogo.vue";
import ImageUploader from "@/components/ImageUploader/ImageUploader.vue";
import { Button, ErrorMessage } from "frappe-ui";
import { useTeam } from "@/stores/team";
import { EditableArea, EditableInput, EditablePreview, EditableRoot } from "reka-ui";
import { ref, watch } from "vue";

const teamStore = useTeam();

const teamName = ref(teamStore.currentTeam?.team_name ?? "");
watch(
    () => teamStore.currentTeam?.team_name,
    (val) => {
        teamName.value = val ?? "";
    }
);

function onSubmit() {
    const trimmed = teamName.value?.trim();
    if (!trimmed || trimmed === teamStore.currentTeam?.team_name) return;
    teamStore.save({ team_name: trimmed });
}
</script>
<template>
    <div class="flex gap-4 w-full">
        <div class="rounded p-4 w-1/6 flex flex-col gap-4 items-center justify-center">
            <TeamLogo
                class-names="h-16 rounded-full"
                :team-name="teamStore.currentTeam!.team_name"
                :logo-url="teamStore.currentTeam?.logo ?? null"
            />
            <ImageUploader
                :crop-dimensions="{ width: 400, height: 400 }"
                :upload-args="{ folder: 'Home' }"
                @success="(file) => teamStore.save({ logo: file.file_url })"
            >
                <template #default="{ uploading, progress, error, openFileSelector }">
                    <ErrorMessage :message="error ?? undefined" />
                    <Button
                        :label="
                            teamStore.currentTeam?.logo
                                ? 'Change'
                                : uploading
                                ? `Uploading ${progress}%`
                                : 'Upload Logo'
                        "
                        icon-left="upload"
                        variant="outline"
                        :loading="uploading"
                        @click="openFileSelector"
                    />
                </template>
            </ImageUploader>
        </div>
        <div class="flex pt-4">
            <EditableRoot
                v-slot="{ isEditing, submit, cancel, edit }"
                v-model="teamName"
                placeholder="Enter team name..."
                class="flex flex-col gap-4"
                auto-resize
                submit-mode="none"
                @submit="onSubmit"
            >
                <EditableArea class="text-2xl font-semibold text-gray-900">
                    <EditablePreview />
                    <EditableInput class="w-full outline-none bg-transparent" />
                </EditableArea>
                <Button
                    v-if="!isEditing"
                    class="max-w-20"
                    label="Edit"
                    variant="outline"
                    @click="edit"
                />
                <div v-else class="flex gap-2">
                    <Button class="max-w-20" label="Save" variant="solid" @click="submit" />
                    <Button
                        class="max-w-20"
                        label="Cancel"
                        theme="red"
                        variant="outline"
                        @click="cancel"
                    />
                </div>
            </EditableRoot>
        </div>
    </div>
</template>
