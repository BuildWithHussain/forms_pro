<template>
    <FormBuilderLayout />
</template>

<script setup lang="ts">
import FormBuilderLayout from "@/layouts/FormBuilderLayout.vue";
import { useRoute } from "vue-router";
import { useEditForm } from "@/stores/editForm";
import { watch, nextTick } from "vue";

const route = useRoute();
const editFormStore = useEditForm();

// Set the form ID when the route changes
watch(
    () => route.params.id,
    async (formId) => {
        if (formId && typeof formId === "string") {
            editFormStore.initialize(formId);
            
            // Check if auto-populate is requested from query params
            if (route.query.autoPopulate === "true") {
                // Wait for form to be loaded
                await nextTick();
                
                // Wait a bit more for the form resource to be ready
                const checkAndPopulate = async () => {
                    if (editFormStore.formResource?.doc?.name) {
                        try {
                            await editFormStore.autoPopulateFieldsFromDoctype(false);
                            // Remove query param after auto-populating
                            if (route.query.autoPopulate) {
                                window.history.replaceState({}, "", route.path);
                            }
                        } catch (error) {
                            // Error is already handled in the store
                        }
                    } else {
                        // Retry after a short delay
                        setTimeout(checkAndPopulate, 200);
                    }
                };
                
                setTimeout(checkAndPopulate, 300);
            }
        }
    },
    { immediate: true }
);
</script>
