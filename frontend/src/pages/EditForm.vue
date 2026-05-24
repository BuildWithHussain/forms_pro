<template>
    <RouteError
        v-if="status === 'error'"
        :exc-type="error?.excType"
        :http-status="error?.httpStatus"
        :messages="error?.messages"
    />
    <FormBuilderLayout v-else />
</template>

<script setup lang="ts">
import FormBuilderLayout from "@/layouts/FormBuilderLayout.vue";
import RouteError from "@/components/RouteError.vue";
import { useRoute } from "vue-router";
import { useEditForm } from "@/stores/editForm";
import { useRouteData } from "@/composables/useRouteData";
import { watch } from "vue";

const route = useRoute();
const editFormStore = useEditForm();
const { status, error } = useRouteData();

// Set the form ID when the route changes
watch(
    () => route.params.id,
    (formId) => {
        if (formId && typeof formId === "string") {
            editFormStore.initialize(formId);
        }
    },
    { immediate: true }
);
</script>
