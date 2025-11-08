<template>
    <div class="table-multiselect-field-wrapper">
        <div class="border rounded-md">
            <div class="p-4 border-b bg-muted/50">
                <h4 class="text-sm font-medium">{{ props.field.label }}</h4>
                <p v-if="props.field.description" class="text-xs text-muted-foreground mt-1">
                    {{ props.field.description }}
                </p>
            </div>
            <div class="p-4">
                <div v-if="selectedItems.length === 0" class="text-sm text-muted-foreground text-center py-4">
                    No items selected
                </div>
                <div v-else class="space-y-2">
                    <div
                        v-for="(item, index) in selectedItems"
                        :key="index"
                        class="flex items-center justify-between p-2 border rounded-md"
                    >
                        <span class="text-sm">{{ formatItem(item) }}</span>
                        <Button variant="ghost" size="sm" @click="removeItem(index)">
                            <X class="h-4 w-4" />
                        </Button>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    class="mt-4"
                    @click="showAddDialog = true"
                >
                    <Plus class="h-4 w-4 mr-2" />
                    Add Item
                </Button>
            </div>
        </div>
        
        <!-- Add Item Dialog -->
        <Dialog v-model:open="showAddDialog">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Add Item</DialogTitle>
                </DialogHeader>
                <div class="py-4">
                    <Combobox
                        v-model="tempSelectedItem"
                        :options="availableOptions"
                        label="Select Item"
                        :loading="optionsLoading"
                        placeholder="Search and select..."
                    />
                </div>
                <DialogFooter>
                    <Button variant="outline" @click="showAddDialog = false">Cancel</Button>
                    <Button @click="addItem">Add</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Combobox } from 'frappe-ui';
import { Plus, X } from 'lucide-vue-next';
import { FormField } from '@/types/formfield';
import { call } from 'frappe-ui';

const props = defineProps<{
    field: FormField;
    modelValue: any[] | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: any[] | null];
}>();

const selectedItems = ref<any[]>(props.modelValue || []);
const showAddDialog = ref(false);
const tempSelectedItem = ref<string | null>(null);
const availableOptions = ref<Array<{ label: string; value: string }>>([]);
const optionsLoading = ref(false);

// Parse options to get child table doctype
const childTableDoctype = computed(() => {
    return props.field.options?.trim() || null;
});

// Load options from child table
watch(() => props.field.options, async () => {
    if (!childTableDoctype.value) return;
    
    try {
        optionsLoading.value = true;
        const response = await call('forms_pro.api.form.get_link_field_options', {
            doctype: childTableDoctype.value,
            fieldname: 'name', // Get all records
        });
        
        if (response && response.options) {
            availableOptions.value = response.options.map((opt: string) => ({
                label: opt,
                value: opt,
            }));
        }
    } catch (error) {
        console.error('Error fetching table multiselect options:', error);
    } finally {
        optionsLoading.value = false;
    }
}, { immediate: true });

watch(() => props.modelValue, (value) => {
    selectedItems.value = value || [];
}, { immediate: true });

function addItem() {
    if (tempSelectedItem.value && !selectedItems.value.includes(tempSelectedItem.value)) {
        selectedItems.value.push(tempSelectedItem.value);
        emit('update:modelValue', selectedItems.value);
        tempSelectedItem.value = null;
        showAddDialog.value = false;
    }
}

function removeItem(index: number) {
    selectedItems.value.splice(index, 1);
    emit('update:modelValue', selectedItems.value.length > 0 ? selectedItems.value : null);
}

function formatItem(item: any): string {
    if (typeof item === 'string') {
        return item;
    }
    return JSON.stringify(item);
}
</script>

