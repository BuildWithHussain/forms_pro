<script setup lang="ts">
import { ref, computed } from "vue";
import { formFields, type FormFields } from "@/utils/form_fields";
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
                    class="flex w-full items-center gap-2 px-2.5 py-2 bg-surface-gray-1 rounded border border-outline-gray-1 hover:border-outline-gray-2 hover:bg-surface-gray-2 active:scale-[0.98] active:bg-surface-gray-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 focus-visible:ring-offset-1 transition-all duration-150 text-left"
                    @click="editFormStore.addField(field.name)"
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
