<script setup lang="ts">
import { useEditForm } from "@/stores/editForm";
import FieldPropertiesForm from "@/components/builder/FieldPropertiesForm.vue";
import { Card, CardContent } from "@/components/ui/card";

const editFormStore = useEditForm();
</script>
<template>
    <div
        class="field-editor-sidebar h-full w-80 border-l border-sidebar-border bg-sidebar flex flex-col"
        data-form-builder-component="field-editor-sidebar"
    >
        <div v-if="!editFormStore.selectedField" class="flex-1 flex items-center justify-center p-4">
            <Card class="w-full">
                <CardContent class="flex flex-col gap-2 p-6 items-center justify-center text-center">
                    <h3 class="text-base font-medium text-muted-foreground">
                        Select a field to edit its properties.
                    </h3>
                </CardContent>
            </Card>
        </div>
        <div class="flex-1 overflow-y-auto" v-else>
            <FieldPropertiesForm v-model="editFormStore.selectedField" />
        </div>
    </div>
</template>
