<script setup>
import { Checkbox, FormControl, Button, Dialog, Combobox, createResource, Select } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { validateFormRoute } from "@/utils/form_generator";
import { ref, computed, watch } from "vue";
import { CircleCheck, Upload } from "lucide-vue-next";

const editFormStore = useEditForm();

const showValidateMsg = ref(false);
const routeExists = ref(false);
const showAutoPopulateDialog = ref(false);
const replaceExisting = ref(false);
const isAutoPopulating = ref(false);
const showChangeDoctypeDialog = ref(false);
const newDoctype = ref(null);
const isUploadingImage = ref(false);
const fileInputRef = ref(null);
const imagePreviewError = ref(false);
const isUploadingLogo = ref(false);
const logoInputRef = ref(null);
const logoPreviewError = ref(false);

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

// Helper function to get image URL
const getImageUrl = (filePath) => {
    if (!filePath) {
        console.log('getImageUrl: No file path provided');
        return '';
    }
    
    console.log('getImageUrl: Input path:', filePath);
    
    // If it's already a full URL, return as is
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        console.log('getImageUrl: Full URL detected, returning as is');
        return filePath;
    }
    
    // If it already starts with /files/, return as is
    if (filePath.startsWith('/files/')) {
        console.log('getImageUrl: /files/ prefix detected, returning as is');
        return filePath;
    }
    
    // If it starts with "files/" (without leading slash), remove it first
    let cleanPath = filePath;
    if (cleanPath.startsWith('files/')) {
        cleanPath = cleanPath.substring(6); // Remove 'files/'
        console.log('getImageUrl: Removed "files/" prefix, clean path:', cleanPath);
    }
    
    // Remove leading slash if present
    if (cleanPath.startsWith('/')) {
        cleanPath = cleanPath.substring(1);
    }
    
    // Construct the URL
    const finalUrl = `/files/${cleanPath}`;
    console.log('getImageUrl: Constructed URL:', finalUrl);
    return finalUrl;
};

// Handle file upload
const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    isUploadingImage.value = true;
    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doctype', 'Form');
        formData.append('docname', editFormStore.formData.name);
        formData.append('fieldname', 'background_image');
        formData.append('folder', 'Home/Attachments');
        formData.append('is_private', '0');
        
        // Upload file using Frappe's file upload endpoint
        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token || frappe?.csrf_token || '',
            },
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error('File upload failed');
        }
        
        const result = await response.json();
        
        console.log('File upload response:', result);
        
        if (result.message) {
            // Frappe returns file info in result.message
            // The file path can be in different fields depending on Frappe version
            let filePath = null;
            
            // Try different possible fields
            if (result.message.file_url) {
                filePath = result.message.file_url;
            } else if (result.message.file_name) {
                filePath = result.message.file_name;
            } else if (result.message.name) {
                filePath = result.message.name;
            } else if (result.message.file) {
                filePath = result.message.file;
            }
            
            console.log('Extracted file path:', filePath);
            
            if (filePath) {
                // Clean the file path - remove any /files/ or files/ prefix
                // We want to store just the relative path (e.g., "pexels-elijah-pilchard-269100825-12792393.jpg")
                if (filePath.startsWith('/files/')) {
                    filePath = filePath.substring(7); // Remove '/files/'
                } else if (filePath.startsWith('files/')) {
                    filePath = filePath.substring(6); // Remove 'files/'
                }
                // Remove leading slash if present
                if (filePath.startsWith('/')) {
                    filePath = filePath.substring(1);
                }
                
                console.log('Cleaned file path (stored in DB):', filePath);
                
                // Reset preview error for new image
                imagePreviewError.value = false;
                // Update the form data with the file path
                editFormStore.formData.background_image = filePath;
                
                // Save the form to persist the change
                await editFormStore.save();
            } else {
                console.error('Upload response structure:', result);
                throw new Error('Could not determine file path from upload response');
            }
        } else {
            console.error('Invalid response structure:', result);
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Failed to upload image. Please try again.');
    } finally {
        isUploadingImage.value = false;
        // Reset file input
        if (fileInputRef.value) {
            fileInputRef.value.value = '';
        }
    }
};

const triggerFileSelect = () => {
    fileInputRef.value?.click();
};

// Font options for selector
const fontOptions = [
    { label: "System Default", value: "System Default" },
    { label: "Arial", value: "Arial" },
    { label: "Helvetica", value: "Helvetica" },
    { label: "Times New Roman", value: "Times New Roman" },
    { label: "Georgia", value: "Georgia" },
    { label: "Verdana", value: "Verdana" },
    { label: "Inter", value: "Inter" },
    { label: "Roboto", value: "Roboto" },
    { label: "Open Sans", value: "Open Sans" },
    { label: "Lato", value: "Lato" },
    { label: "Montserrat", value: "Montserrat" },
    { label: "Merriweather", value: "Merriweather" },
    { label: "Playfair Display", value: "Playfair Display" },
    { label: "Lora", value: "Lora" },
    { label: "Courier New", value: "Courier New" },
    { label: "Monaco", value: "Monaco" },
];

// Handle logo upload
const handleLogoSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    isUploadingLogo.value = true;
    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doctype', 'Form');
        formData.append('docname', editFormStore.formData.name);
        formData.append('fieldname', 'logo');
        formData.append('folder', 'Home/Attachments');
        formData.append('is_private', '0');
        
        // Upload file using Frappe's file upload endpoint
        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token || frappe?.csrf_token || '',
            },
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error('File upload failed');
        }
        
        const result = await response.json();
        
        console.log('Logo upload response:', result);
        
        if (result.message) {
            let filePath = null;
            
            // Try different possible fields
            if (result.message.file_url) {
                filePath = result.message.file_url;
            } else if (result.message.file_name) {
                filePath = result.message.file_name;
            } else if (result.message.name) {
                filePath = result.message.name;
            } else if (result.message.file) {
                filePath = result.message.file;
            }
            
            console.log('Extracted logo file path:', filePath);
            
            if (filePath) {
                // Clean the file path - remove any /files/ or files/ prefix
                if (filePath.startsWith('/files/')) {
                    filePath = filePath.substring(7);
                } else if (filePath.startsWith('files/')) {
                    filePath = filePath.substring(6);
                }
                if (filePath.startsWith('/')) {
                    filePath = filePath.substring(1);
                }
                
                console.log('Cleaned logo file path (stored in DB):', filePath);
                
                // Reset preview error for new logo
                logoPreviewError.value = false;
                // Update the form data with the file path
                editFormStore.formData.logo = filePath;
                
                // Save the form to persist the change
                await editFormStore.save();
            } else {
                console.error('Logo upload response structure:', result);
                throw new Error('Could not determine file path from upload response');
            }
        } else {
            console.error('Invalid logo upload response structure:', result);
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Error uploading logo:', error);
        alert('Failed to upload logo. Please try again.');
    } finally {
        isUploadingLogo.value = false;
        // Reset file input
        if (logoInputRef.value) {
            logoInputRef.value.value = '';
        }
    }
};

const triggerLogoSelect = () => {
    logoInputRef.value?.click();
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

            <h5 class="text-sm font-medium mt-6 mb-1">Form Styling</h5>
            <div class="space-y-4">
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Background Image</label>
                    <input
                        ref="fileInputRef"
                        type="file"
                        accept="image/*"
                        @change="handleFileSelect"
                        class="hidden"
                    />
                    <Button
                        variant="outline"
                        @click="triggerFileSelect"
                        :loading="isUploadingImage"
                        class="w-full"
                        :icon="Upload"
                    >
                        {{ isUploadingImage ? 'Uploading...' : (editFormStore.formData.background_image ? 'Change Image' : 'Upload Image') }}
                    </Button>
                    <div v-if="editFormStore.formData.background_image" class="mt-2">
                        <div class="relative w-full h-32 rounded border border-gray-200 overflow-hidden bg-gray-100">
                            <img 
                                v-if="!imagePreviewError"
                                :src="getImageUrl(editFormStore.formData.background_image)" 
                                alt="Background preview"
                                class="w-full h-full object-cover"
                                @error="imagePreviewError = true"
                                @load="imagePreviewError = false"
                            />
                            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                                <div class="text-center">
                                    <Upload class="w-8 h-8 mx-auto mb-1" />
                                    <p class="text-xs">Preview unavailable</p>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center justify-between mt-2">
                            <p class="text-xs text-gray-500 truncate flex-1">
                                {{ editFormStore.formData.background_image }}
                            </p>
                            <Button
                                variant="ghost"
                                size="sm"
                                @click="editFormStore.formData.background_image = null; editFormStore.save(); imagePreviewError = false"
                                class="text-red-500"
                            >
                                Remove
                            </Button>
                        </div>
                    </div>
                    <p class="text-xs text-gray-500">
                        Upload an image file for the form background
                    </p>
                </div>
                
                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Background Color</label>
                    <div class="flex gap-2">
                        <input
                            type="color"
                            v-model="editFormStore.formData.background_color"
                            class="w-12 h-10 rounded border border-gray-300 cursor-pointer"
                        />
                        <FormControl
                            variant="outline"
                            type="text"
                            v-model="editFormStore.formData.background_color"
                            placeholder="#ffffff"
                            class="flex-1"
                        />
                    </div>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Theme Color</label>
                    <div class="flex gap-2">
                        <input
                            type="color"
                            v-model="editFormStore.formData.theme_color"
                            class="w-12 h-10 rounded border border-gray-300 cursor-pointer"
                        />
                        <FormControl
                            variant="outline"
                            type="text"
                            v-model="editFormStore.formData.theme_color"
                            placeholder="#3b82f6"
                            class="flex-1"
                        />
                    </div>
                </div>

                <Checkbox
                    size="sm"
                    label="Enable Glass Morphism"
                    variant="outline"
                    v-model="editFormStore.formData.glass_morphism_enabled"
                />

                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Overlay Opacity</label>
                    <div class="flex gap-2 items-center">
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            v-model.number="editFormStore.formData.overlay_opacity"
                            class="flex-1"
                        />
                        <span class="text-xs text-gray-500 w-12 text-right">
                            {{ (editFormStore.formData.overlay_opacity || 0.5) * 100 }}%
                        </span>
                    </div>
                    <p class="text-xs text-gray-500">
                        Adjust the opacity of the background overlay for better text readability
                    </p>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Font Family</label>
                    <Select
                        v-model="editFormStore.formData.font_family"
                        :options="fontOptions"
                        variant="outline"
                    />
                    <p class="text-xs text-gray-500">
                        Choose a font family for the form text
                    </p>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium">Logo</label>
                    <input
                        ref="logoInputRef"
                        type="file"
                        accept="image/*"
                        @change="handleLogoSelect"
                        class="hidden"
                    />
                    <Button
                        variant="outline"
                        @click="triggerLogoSelect"
                        :loading="isUploadingLogo"
                        class="w-full"
                        :icon="Upload"
                    >
                        {{ isUploadingLogo ? 'Uploading...' : (editFormStore.formData.logo ? 'Change Logo' : 'Upload Logo') }}
                    </Button>
                    <div v-if="editFormStore.formData.logo" class="mt-2">
                        <div class="relative w-full h-20 rounded border border-gray-200 overflow-hidden bg-gray-100 flex items-center justify-center">
                            <img 
                                v-if="!logoPreviewError"
                                :src="getImageUrl(editFormStore.formData.logo)" 
                                alt="Logo preview"
                                class="max-w-full max-h-full object-contain"
                                @error="logoPreviewError = true"
                                @load="logoPreviewError = false"
                            />
                            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                                <div class="text-center">
                                    <Upload class="w-6 h-6 mx-auto mb-1" />
                                    <p class="text-xs">Preview unavailable</p>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center justify-between mt-2">
                            <p class="text-xs text-gray-500 truncate flex-1">
                                {{ editFormStore.formData.logo }}
                            </p>
                            <Button
                                variant="ghost"
                                size="sm"
                                @click="editFormStore.formData.logo = null; editFormStore.save(); logoPreviewError = false"
                                class="text-red-500"
                            >
                                Remove
                            </Button>
                        </div>
                    </div>
                    <p class="text-xs text-gray-500">
                        Upload a logo to display on the form header
                    </p>
                </div>
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
