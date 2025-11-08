<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { createResource, Button } from "frappe-ui";
import { Plus, Trash2 } from "lucide-vue-next";
import RenderField from "@/components/RenderField.vue";
import { FormField } from "@/types/formfield";

const props = defineProps<{
    field: FormField;
    modelValue: any[];
    parentDoctype?: string;
    themeColor?: string;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: any[]];
}>();

// Fetch child table field definitions
const childTableFields = createResource({
    url: "forms_pro.api.form.get_child_table_fields",
    makeParams: () => ({
        child_doctype: props.field.options,
    }),
    auto: true,
    // No transform needed - createResource from frappe-ui automatically unwraps { message: [...] }
    // The API returns a list directly, and createResource unwraps it
});

// Table rows data
const rows = ref<any[]>(props.modelValue || []);

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
    if (newValue && Array.isArray(newValue)) {
        rows.value = newValue;
    }
}, { deep: true });

// Emit changes when rows change
watch(rows, (newRows) => {
    emit("update:modelValue", newRows);
}, { deep: true });

// Add a new row
const addRow = () => {
    const newRow: any = {};
    const fieldsList = fields.value;
    if (fieldsList && fieldsList.length > 0) {
        fieldsList.forEach((field: FormField) => {
            newRow[field.fieldname] = field.default || "";
        });
    }
    rows.value.push(newRow);
};

// Remove a row
const removeRow = (index: number) => {
    rows.value.splice(index, 1);
};

// Update a cell value
const updateCell = (rowIndex: number, fieldname: string, value: any) => {
    if (!rows.value[rowIndex]) {
        rows.value[rowIndex] = {};
    }
    rows.value[rowIndex][fieldname] = value;
};

// Get cell value
const getCellValue = (rowIndex: number, fieldname: string) => {
    return rows.value[rowIndex]?.[fieldname] || "";
};

const isLoading = computed(() => childTableFields.loading);
const fields = computed(() => {
    // createResource from frappe-ui automatically unwraps { message: [...] } from API responses
    // So childTableFields.data is already the array of fields
    const data = childTableFields.data;
    
    // Debug logging
    if (props.field.options && !data && !isLoading.value) {
        console.warn('[TableField] No data received for child doctype:', props.field.options);
        console.warn('[TableField] Resource error:', childTableFields.error);
    }
    
    if (!data) return [];
    
    // Data should already be an array (unwrapped by createResource)
    if (Array.isArray(data)) {
        return data;
    }
    
    // Fallback: if somehow it's still wrapped, try to unwrap it
    if (data?.message && Array.isArray(data.message)) {
        return data.message;
    }
    
    // If data exists but isn't an array, log warning
    if (data) {
        console.warn('[TableField] Expected array but got:', typeof data, data);
    }
    
    return [];
});
</script>

<template>
    <div class="table-field-wrapper">
        <div v-if="isLoading" class="p-4 text-center text-gray-500">
            Loading table structure...
        </div>
        
        <div v-else-if="fields.length === 0" class="p-4 text-center text-gray-500">
            No fields found for this table
        </div>
        
        <div v-else class="space-y-4">
            <!-- Table Header -->
            <div class="flex items-center justify-between">
                <label class="text-sm font-medium">
                    {{ field.label }}
                    <span v-if="field.reqd" class="text-red-500">*</span>
                </label>
                <Button
                    variant="outline"
                    size="sm"
                    :icon="Plus"
                    @click="addRow"
                >
                    Add Row
                </Button>
            </div>
            
            <!-- Empty State -->
            <div v-if="rows.length === 0" class="p-8 border border-dashed border-gray-300 rounded-lg text-center">
                <p class="text-gray-500 mb-4">No rows added yet</p>
                <Button
                    variant="outline"
                    size="sm"
                    :icon="Plus"
                    @click="addRow"
                >
                    Add First Row
                </Button>
            </div>
            
            <!-- Table -->
            <div v-else class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <!-- Table Header -->
                        <thead class="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th
                                    v-for="childField in fields"
                                    :key="childField.fieldname"
                                    class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase"
                                >
                                    {{ childField.label }}
                                    <span v-if="childField.reqd" class="text-red-500">*</span>
                                </th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase w-20">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        
                        <!-- Table Body -->
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="(row, rowIndex) in rows" :key="rowIndex" class="hover:bg-gray-50">
                                <td
                                    v-for="childField in fields"
                                    :key="childField.fieldname"
                                    class="px-4 py-2"
                                >
                                    <!-- Render child field without label or description (label is in table header) -->
                                    <RenderField
                                        :field="{ ...childField, label: '', description: '' }"
                                        :model-value="getCellValue(rowIndex, childField.fieldname)"
                                        @update:model-value="(value) => updateCell(rowIndex, childField.fieldname, value)"
                                        :parent-doctype="parentDoctype"
                                        :theme-color="themeColor"
                                    />
                                </td>
                                <td class="px-4 py-2">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        :icon="Trash2"
                                        @click="removeRow(rowIndex)"
                                        class="text-red-500 hover:text-red-700"
                                    />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Description -->
            <p v-if="field.description" class="text-xs text-gray-500">
                {{ field.description }}
            </p>
        </div>
    </div>
</template>

<style scoped>
.table-field-wrapper {
    width: 100%;
}

table {
    border-collapse: collapse;
}

th {
    white-space: nowrap;
}

td {
    vertical-align: top;
}
</style>

