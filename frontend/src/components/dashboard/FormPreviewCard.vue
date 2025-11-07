<script setup>
import { Badge, Button, Dialog, call } from "frappe-ui";
import { computed, ref } from "vue";
import { Trash2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import { useRouter } from "vue-router";

const props = defineProps({
    form: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["deleted"]);
const router = useRouter();

const showDeleteDialog = ref(false);
const isDeleting = ref(false);

const formattedDate = computed(() => {
    return new Date(props.form.creation).toLocaleDateString();
});

const handleDelete = async () => {
    isDeleting.value = true;
    try {
        await call("forms_pro.api.form.delete_form", {
            form_id: props.form.name,
        });
        
        toast.success("Form deleted successfully");
        showDeleteDialog.value = false;
        emit("deleted", props.form.name);
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "An error occurred";
        toast.error("Failed to delete form", {
            description: errorMessage,
        });
    } finally {
        isDeleting.value = false;
    }
};

const handleCardClick = (event) => {
    // Don't navigate if clicking on the delete button
    const target = event.target;
    if (target.closest(".delete-button") || target.closest(".delete-icon")) {
        return;
    }
    // Don't navigate if clicking on the dialog
    if (target.closest(".delete-dialog")) {
        return;
    }
    // Navigate to edit form
    router.push({ name: "Edit Form", params: { id: props.form.name } });
};
</script>
<template>
    <div class="relative">
        <div
            @click="handleCardClick"
            class="flex flex-col gap-2 border rounded p-4 hover:border-gray-400 transition-all duration-300 cursor-pointer"
        >
            <div class="flex flex-col gap-3">
                <div class="flex justify-between items-start">
                    <h3 class="text-lg font-medium">{{ props.form.title }}</h3>
                    <Button
                        class="delete-button"
                        variant="ghost"
                        size="sm"
                        @click.stop="showDeleteDialog = true"
                        :icon="Trash2"
                        iconOnly
                    />
                </div>
                <div class="flex gap-2 items-center">
                    <Badge
                        class="w-fit"
                        :label="props.form.is_published ? 'Published' : 'Draft'"
                        :theme="props.form.is_published ? 'green' : 'gray'"
                    />
                    <p class="text-sm text-gray-500">{{ formattedDate }}</p>
                </div>
            </div>
        </div>
        
        <Dialog
            v-model="showDeleteDialog"
            :options="{
                title: 'Delete Form',
            }"
            class="delete-dialog"
        >
            <template #body-content>
                <p class="text-sm text-gray-600">
                    Are you sure you want to delete "{{ props.form.title }}"? This action cannot be undone.
                </p>
            </template>
            <template #actions="{ close }">
                <div class="flex gap-2 w-full">
                    <Button
                        variant="outline"
                        class="flex-1"
                        @click="close"
                        :disabled="isDeleting"
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="solid"
                        class="flex-1"
                        @click="handleDelete"
                        :loading="isDeleting"
                    >
                        Delete
                    </Button>
                </div>
            </template>
        </Dialog>
    </div>
</template>
