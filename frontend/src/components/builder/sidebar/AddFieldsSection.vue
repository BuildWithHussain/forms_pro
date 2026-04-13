<script setup lang="ts">
import { ref, computed } from "vue";
import { formFields, FormFields } from "@/utils/form_fields";
import { Fieldtype } from "@/types/formfield";
import { FormControl, Button } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import RenderField from "@/components/RenderField.vue";
import type { Component } from "vue";

const search = ref("");
const componentMap = formFields.reduce((acc: Record<string, Component>, field: FormFields) => {
    acc[field.name] = field.component;
    return acc;
}, {});

const filteredComponents = computed(() => {
    return Object.keys(componentMap).filter((component) =>
        component.toLowerCase().includes(search.value.toLowerCase())
    );
});

const editFormStore = useEditForm();
</script>
<template>
    <div class="space-y-4">
        <h3 class="text-lg font-medium">Add Fields</h3>
        <div class="flex flex-col gap-3">
            <FormControl
                v-model="search"
                type="search"
                variant="outline"
                placeholder="Search Fields"
            />
            <div v-for="component in filteredComponents" :key="component">
                <div
                    :data-testid="`field-type-${component}`"
                    class="p-2 bg-gray-50 w-full rounded flex flex-col gap-2 border border-gray-200 hover:border-gray-400 transition-all relative group"
                >
                    <div class="text-sm">{{ component }}</div>
                    <RenderField class="pointer-events-none" :field="{ fieldtype: component }" />
                    <Button
                        class="absolute top-4 -right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                        variant="outline"
                        icon="plus"
                        @click="editFormStore.addField(component as Fieldtype)"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
