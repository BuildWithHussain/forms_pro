<script setup lang="ts">
import { Dialog, ErrorMessage, FormControl } from "frappe-ui";
import * as z from "zod";
import { reactive, ref, watch } from "vue";
import { useUser } from "@/stores/user";

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
});

type Form = z.infer<typeof formSchema>;

const form = reactive<Form>({
    team_name: "",
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
    user.createTeam(form.team_name);
    model.value = false;
}
</script>
<template>
    <Dialog
        v-model="model"
        :options="{
            title: 'Create New Team',
            icon: 'users',
        }"
    >
        <template #body-content>
            <div class="flex flex-col gap-4">
                <FormControl
                    v-model="form.team_name"
                    label="Team Name"
                    variant="outline"
                    type="text"
                    required
                />
                <ErrorMessage :message="formErrors" />
                <Button @click="createTeam" :disabled="formErrors !== ''" variant="subtle">
                    Create Team
                </Button>
            </div>
        </template>
    </Dialog>
</template>
