<script setup lang="ts">
import { ref, computed } from "vue";
import { formFields, FormFields } from "@/utils/form_fields";
import { Fieldtype } from "@/types/formfield";
import { FormControl } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";

const search = ref("");

const filteredFields = computed(() => {
    const q = search.value.toLowerCase();
    return formFields.filter((field: FormFields) => field.name.toLowerCase().includes(q));
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
            <div class="flex flex-col gap-2">
                <button
                    v-for="field in filteredFields"
                    :key="field.name"
                    type="button"
                    class="flex items-center gap-2 p-2 bg-gray-50 rounded border border-gray-200 hover:border-gray-400 hover:bg-gray-100 transition-all text-left"
                    @click="editFormStore.addField(field.name as Fieldtype)"
                >
                    <component :is="field.icon" class="w-4 h-4 text-gray-600 shrink-0" />
                    <span class="text-sm truncate">{{ field.name }}</span>
                </button>
            </div>
        </div>
    </div>
</template>
