<script setup lang="ts">
import { useCall, Button } from "frappe-ui";
import { computed } from "vue";
import FieldRenderer from "../builder/FieldRenderer.vue";
import { mapDoctypeFieldForForm } from "@/utils/form_fields";

type Row = {
    [key: string]: any;
};

const rows = defineModel<Row[]>({ default: [] });

type props = {
    inEditMode: boolean;
    doctype: string;
};

const props = defineProps<props>();

const columnResource = useCall({
    url: "forms_pro.api.form.get_doctype_fields",
    baseUrl: "/api/v2/method/",
    params: {
        doctype: props.doctype,
    },
});

const columns = computed(() => {
    const data = columnResource.data;
    if (!Array.isArray(data)) {
        return [];
    }
    return data.map((column: any) => ({
        label: column.label,
        key: column.fieldname,
        ...column,
        fieldtype: mapDoctypeFieldForForm(column.fieldtype) ?? "Data",
    }));
});

function addRow() {
    const newRow = columns.value.reduce((acc, column) => {
        acc[column.key] = null;
        return acc;
    }, {} as Row);
    rows.value = [...(rows.value ?? []), newRow];
}

function removeRow(index: number) {
    rows.value = rows.value?.filter((_, i) => i !== index) ?? [];
}

function updateCell(rowIndex: number, key: string, value: unknown) {
    const list = rows.value ?? [];
    if (rowIndex < 0 || rowIndex >= list.length) return;
    rows.value = list.map((row, i) => (i === rowIndex ? { ...row, [key]: value } : row));
}
</script>
<template>
    <div class="flex flex-col gap-5 p-4 bg-surface-gray-1 border rounded">
        <div v-if="!rows.length" class="flex flex-col gap-2 items-center justify-center">
            <h5 class="text-base font-medium text-ink-gray-6">No rows added</h5>
            <p class="text-sm text-ink-gray-5">Add an item to get started</p>
        </div>
        <div
            v-for="(_, index) in rows"
            :key="index"
            class="border-b border-gray-400 pb-4 border p-4 rounded bg-surface-white relative"
        >
            <Button
                icon="x"
                variant="outline"
                class="absolute -top-2 -right-2 w-4 h-4"
                @click="removeRow(index)"
            />
            <FieldRenderer
                v-for="column in columns"
                :key="column.key"
                :model-value="rows[index][column.key]"
                @update:model-value="updateCell(index, column.key, $event)"
                :field="column"
                :in-edit-mode="false"
            />
        </div>
    </div>
    <Button v-if="!inEditMode" @click="addRow">Add Row</Button>
</template>
