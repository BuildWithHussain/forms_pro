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
            <p v-if="!filteredFields.length" class="text-sm text-gray-500 px-1 py-2">
                No fields match "{{ search }}"
            </p>
            <div v-else class="flex flex-col gap-2">
                <button
                    v-for="field in filteredFields"
                    :key="field.name"
                    type="button"
                    :title="field.name"
                    class="flex items-center gap-2 px-2.5 py-2 bg-gray-50 rounded border border-gray-200 hover:border-gray-400 hover:bg-gray-100 active:scale-[0.98] active:bg-gray-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 focus-visible:ring-offset-1 transition-colors duration-150 text-left"
                    @click="editFormStore.addField(field.name as Fieldtype)"
                >
                    <component
                        :is="field.icon"
                        class="w-4 h-4 text-gray-600 shrink-0"
                        aria-hidden="true"
                    />
                    <span class="text-sm truncate">{{ field.name }}</span>
                </button>
            </div>
        </div>
    </div>
</template>
