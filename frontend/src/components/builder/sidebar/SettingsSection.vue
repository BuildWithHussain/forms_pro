<script setup>
import { Checkbox, FormControl, Button, Dialog, Combobox, createResource } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { validateFormRoute } from "@/utils/form_generator";
import { ref, computed, watch } from "vue";
import { CircleCheck } from "lucide-vue-next";

const editFormStore = useEditForm();

const showValidateMsg = ref(false);
const routeExists = ref(false);
const showAutoPopulateDialog = ref(false);
const replaceExisting = ref(false);
const isAutoPopulating = ref(false);
const showChangeDoctypeDialog = ref(false);
const newDoctype = ref(null);

// Load doctype list
const doctypes = createResource({
    url: "forms_pro.api.form.get_doctype_list",
    auto: true,
    transform: (data) => {
        // Ensure we always return an array
        return Array.isArray(data) ? data : [];
    },
});

const canAutoPopulate = computed(() => {
    return (
        editFormStore.formData?.linked_doctype &&
        !editFormStore.isPublished &&
        !isAutoPopulating.value
    );
});

const canChangeDoctype = computed(() => {
    return !editFormStore.isPublished;
});

const hasExistingFields = computed(() => {
    return editFormStore.fields && editFormStore.fields.length > 0;
});

const validateRoute = async () => {
    routeExists.value = await validateFormRoute(
        editFormStore.formData.name,
        editFormStore.formData.route
    );
    showValidateMsg.value = true;
};

const handleAutoPopulate = async () => {
    if (!canAutoPopulate.value) return;

    isAutoPopulating.value = true;
    try {
        await editFormStore.autoPopulateFieldsFromDoctype(replaceExisting.value);
        showAutoPopulateDialog.value = false;
        replaceExisting.value = false;
    } catch (error) {
        // Error is already handled in the store
    } finally {
        isAutoPopulating.value = false;
    }
};

const handleDoctypeChange = (newValue) => {
    const currentDoctype = editFormStore.formData?.linked_doctype;
    
    // If no change or empty, do nothing
    if (!newValue || newValue === currentDoctype) {
        return;
    }
    
    // Store the new value
    newDoctype.value = newValue;
    
    // Revert the combobox to current value temporarily
    editFormStore.formData.linked_doctype = currentDoctype;
    
    // Check if form has existing fields
    if (hasExistingFields.value) {
        showChangeDoctypeDialog.value = true;
    } else {
        updateDoctype();
    }
};

const updateDoctype = async () => {
    if (!newDoctype.value) return;
    
    try {
        // Ensure title is not empty before updating
        const currentTitle = editFormStore.formData?.title || "Untitled Form";
        
        // Update the linked_doctype along with title to avoid mandatory error
        await editFormStore.formResource.setValue.submit({
            linked_doctype: newDoctype.value,
            title: currentTitle, // Ensure title is preserved
        });
        
        // Update the form data
        editFormStore.formData.linked_doctype = newDoctype.value;
        
        // Reload doctype fields
        await editFormStore.getDoctypeFields();
        
        showChangeDoctypeDialog.value = false;
        newDoctype.value = null;
    } catch (error) {
        // Error handling - revert to original
        editFormStore.reload();
        console.error("Failed to update doctype:", error);
    }
};
</script>
<template>
    <div class="space-y-4">
        <h3 class="text-lg font-medium">Settings</h3>
        <div class="flex flex-col gap-3">
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium">Linked DocType</label>
                <Combobox
                    v-model="editFormStore.formData.linked_doctype"
                    :options="doctypes.data || []"
                    label="DocType"
                    :disabled="!canChangeDoctype || doctypes.loading"
                    :loading="doctypes.loading"
                    @update:modelValue="handleDoctypeChange"
                />
                <p v-if="!canChangeDoctype" class="text-xs text-gray-500">
                    Cannot change DocType for published forms
                </p>
                <p v-if="doctypes.loading" class="text-xs text-gray-500">
                    Loading DocTypes...
                </p>
            </div>
            <FormControl
                label="Form ID"
                variant="outline"
                type="text"
                v-model="editFormStore.formData.name"
                disabled
            />

            <h5 class="text-sm font-medium mt-4 mb-1">Form Properties</h5>
            <div class="space-y-6">
                <FormControl
                    required
                    label="Route"
                    variant="outline"
                    type="text"
                    v-model="editFormStore.formData.route"
                    description="Set a unique route for the form."
                    @change="validateRoute()"
                />
                <div v-if="showValidateMsg" class="text-xs font-medium">
                    <span v-if="routeExists" class="text-red-500 flex items-center gap-1">
                        Route already exists
                    </span>
                    <span v-else class="text-green-500 flex items-center gap-1">
                        <CircleCheck class="w-4 h-4" /> Route is available</span
                    >
                </div>
                <Checkbox
                    size="sm"
                    label="Allow Incomplete Forms"
                    variant="outline"
                    v-model="editFormStore.formData.allow_incomplete"
                />
            </div>

            <h5 class="text-sm font-medium mt-6 mb-1">Auto-populate Fields</h5>
            <div class="space-y-3">
                <p class="text-xs text-gray-500">
                    Automatically add all fields from the linked DocType to your form.
                </p>
                <Button
                    variant="outline"
                    :disabled="!canAutoPopulate"
                    @click="showAutoPopulateDialog = true"
                    class="w-full"
                >
                    Auto-populate from DocType
                </Button>
            </div>
        </div>
    </div>

    <Dialog
        v-model="showAutoPopulateDialog"
        :options="{
            title: 'Auto-populate Fields',
        }"
    >
        <template #body-content>
            <div class="flex flex-col gap-4">
                <p class="text-sm text-gray-600">
                    This will add all fields from the linked DocType to your form.
                </p>
                <Checkbox
                    v-model="replaceExisting"
                    label="Replace existing fields"
                    description="If checked, all current fields will be removed and replaced with DocType fields."
                />
            </div>
        </template>
        <template #actions="{ close }">
            <div class="flex gap-2 w-full">
                <Button variant="outline" @click="close" class="flex-1">
                    Cancel
                </Button>
                <Button
                    variant="solid"
                    @click="handleAutoPopulate"
                    :loading="isAutoPopulating"
                    class="flex-1"
                >
                    {{ replaceExisting ? "Replace Fields" : "Add Fields" }}
                </Button>
            </div>
        </template>
    </Dialog>

    <Dialog
        v-model="showChangeDoctypeDialog"
        :options="{
            title: 'Change Linked DocType',
        }"
    >
        <template #body-content>
            <div class="flex flex-col gap-4">
                <p class="text-sm text-gray-600">
                    This form already has {{ editFormStore.fields.length }} field(s). Changing the DocType will not remove existing fields, but you may want to update them manually or use auto-populate with the new DocType.
                </p>
                <p class="text-sm font-medium">
                    Current DocType: <span class="text-gray-600">{{ editFormStore.formData.linked_doctype }}</span>
                </p>
                <p class="text-sm font-medium">
                    New DocType: <span class="text-gray-600">{{ newDoctype }}</span>
                </p>
            </div>
        </template>
        <template #actions="{ close }">
            <div class="flex gap-2 w-full">
                <Button variant="outline" @click="close" class="flex-1">
                    Cancel
                </Button>
                <Button
                    variant="solid"
                    @click="updateDoctype"
                    class="flex-1"
                >
                    Change DocType
                </Button>
            </div>
        </template>
    </Dialog>
</template>
