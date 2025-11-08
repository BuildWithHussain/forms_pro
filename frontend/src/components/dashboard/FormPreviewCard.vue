<script setup>
import { Badge, Button, Dialog, call } from "frappe-ui";
import { computed, ref, watch, nextTick, onMounted } from "vue";
import { Trash2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import { useRouter } from "vue-router";

const props = defineProps({
    form: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["deleted"]);
const router = useRouter();

const showDeleteDialog = ref(false);
const isDeleting = ref(false);

// Function to center dialog
const centerDialog = () => {
    nextTick(() => {
        // Find all dialogs with delete-dialog class
        const dialogs = document.querySelectorAll('.delete-dialog, .delete-dialog-centered, [role="dialog"]');
        dialogs.forEach((dialog) => {
            const htmlEl = dialog;
            if (!(htmlEl instanceof HTMLElement)) return;
            
            const computedStyle = window.getComputedStyle(htmlEl);
            
            // Only fix if it's not already centered
            if (computedStyle.position === 'fixed' || computedStyle.position === 'absolute') {
                htmlEl.style.setProperty('position', 'fixed', 'important');
                htmlEl.style.setProperty('top', '50%', 'important');
                htmlEl.style.setProperty('left', '50%', 'important');
                htmlEl.style.setProperty('transform', 'translate(-50%, -50%)', 'important');
                htmlEl.style.setProperty('margin', '0', 'important');
                htmlEl.style.setProperty('z-index', '9999', 'important');
            }
        });
    });
};

// Watch for dialog opening
watch(showDeleteDialog, (isOpen) => {
    if (isOpen) {
        // Center immediately and on next tick
        centerDialog();
        setTimeout(centerDialog, 10);
        setTimeout(centerDialog, 50);
        setTimeout(centerDialog, 100);
        
        // Also use MutationObserver to catch when dialog is added to DOM
        const observer = new MutationObserver(() => {
            centerDialog();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
        
        // Clean up observer after a short delay
        setTimeout(() => {
            observer.disconnect();
        }, 500);
    }
});

const formattedDate = computed(() => {
    return new Date(props.form.creation).toLocaleDateString();
});

// Helper to get image URL
const getImageUrl = (filePath) => {
    if (!filePath) return null;
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        return filePath;
    }
    if (filePath.startsWith('/files/')) {
        return filePath;
    }
    if (filePath.startsWith('files/')) {
        return '/' + filePath;
    }
    // Remove leading slashes and add /files/ prefix
    const cleanPath = filePath.replace(/^\/+/, '');
    return '/files/' + cleanPath;
};

// Preview styles
const previewStyles = computed(() => {
    const bgColor = props.form.background_color || "#ffffff";
    const bgImage = props.form.background_image;
    
    const styles = {
        backgroundColor: bgColor,
    };
    
    if (bgImage) {
        const imageUrl = getImageUrl(bgImage);
        styles.backgroundImage = `url(${imageUrl})`;
        styles.backgroundSize = "cover";
        styles.backgroundPosition = "center";
        styles.backgroundRepeat = "no-repeat";
    }
    
    return styles;
});

const containerStyles = computed(() => {
    const styles = {
        backgroundColor: props.form.background_color || "#ffffff",
    };
    
    if (props.form.glass_morphism_enabled) {
        styles.backgroundColor = "rgba(255, 255, 255, 0.1)";
        styles.backdropFilter = "blur(10px)";
        styles.border = "1px solid rgba(255, 255, 255, 0.2)";
    } else {
        styles.border = "1px solid rgba(0, 0, 0, 0.1)";
    }
    
    return styles;
});

const themeColor = computed(() => props.form.theme_color || "#3b82f6");
const hasFields = computed(() => props.form.fields && Array.isArray(props.form.fields) && props.form.fields.length > 0);
const previewFields = computed(() => {
    if (!hasFields.value) return [];
    // Show first 4-5 fields for preview
    return props.form.fields.slice(0, 5);
});

// Get font family for preview
const fontFamily = computed(() => {
    const font = props.form.font_family;
    if (!font || font === "System Default") return null;
    return font;
});

const handleDelete = async () => {
    isDeleting.value = true;
    try {
        await call("forms_pro.api.form.delete_form", {
            form_id: props.form.name,
        });
        
        toast.success("Form deleted successfully");
        showDeleteDialog.value = false;
        emit("deleted", props.form.name);
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "An error occurred";
        toast.error("Failed to delete form", {
            description: errorMessage,
        });
    } finally {
        isDeleting.value = false;
    }
};

const handleCardClick = (event) => {
    // Don't navigate if clicking on the delete button
    const target = event.target;
    if (target.closest(".delete-button") || target.closest(".delete-icon")) {
        return;
    }
    // Don't navigate if clicking on the dialog
    if (target.closest(".delete-dialog")) {
        return;
    }
    // Navigate to edit form
    router.push({ name: "Edit Form", params: { id: props.form.name } });
};
</script>
<template>
    <div class="relative">
        <div
            @click="handleCardClick"
            class="flex flex-col gap-3 border rounded-lg overflow-hidden hover:border-gray-400 hover:shadow-lg transition-all duration-300 cursor-pointer bg-white"
        >
            <!-- Form Preview -->
            <div 
                class="relative h-48 overflow-hidden"
                :style="previewStyles"
            >
                <!-- Overlay for background image -->
                <div
                    v-if="props.form.background_image"
                    class="absolute inset-0"
                    :style="{
                        backgroundColor: `rgba(0, 0, 0, ${(props.form.overlay_opacity || 0.5) * 0.3})`,
                    }"
                ></div>
                
                <!-- Preview Content -->
                <div 
                    class="relative h-full p-4 flex flex-col gap-2.5"
                    :style="{ ...containerStyles, fontFamily: fontFamily }"
                >
                    <!-- Title and Logo -->
                    <div class="flex items-start justify-between gap-2 mb-1">
                        <h3 
                            class="text-sm font-bold truncate flex-1 leading-tight"
                            :style="{ color: themeColor }"
                        >
                            {{ props.form.title || "Untitled Form" }}
                        </h3>
                        <img 
                            v-if="props.form.logo"
                            :src="getImageUrl(props.form.logo)"
                            alt="Logo"
                            class="w-10 h-5 object-contain flex-shrink-0"
                            style="max-width: 60px;"
                        />
                    </div>
                    
                    <!-- Field Previews with Labels -->
                    <div class="flex flex-col gap-2 flex-1 overflow-hidden">
                        <div 
                            v-for="(field, idx) in previewFields"
                            :key="idx"
                            class="flex flex-col gap-1"
                        >
                            <!-- Field Label -->
                            <div 
                                class="text-[9px] font-medium leading-tight truncate"
                                :style="{
                                    color: props.form.glass_morphism_enabled 
                                        ? 'rgba(0, 0, 0, 0.8)' 
                                        : 'rgba(0, 0, 0, 0.6)',
                                }"
                            >
                                {{ field.label || field.fieldname }}
                            </div>
                            <!-- Field Input Preview -->
                            <div 
                                class="h-4 rounded border"
                                :style="{
                                    backgroundColor: props.form.glass_morphism_enabled 
                                        ? 'rgba(255, 255, 255, 0.4)' 
                                        : 'rgba(255, 255, 255, 0.9)',
                                    borderColor: props.form.glass_morphism_enabled 
                                        ? 'rgba(255, 255, 255, 0.3)' 
                                        : 'rgba(0, 0, 0, 0.1)',
                                    width: field.fieldtype === 'Textarea' || field.fieldtype === 'Text Editor' ? '100%' : '85%',
                                }"
                            >
                                <!-- Dropdown indicator for Select/Link fields -->
                                <div 
                                    v-if="field.fieldtype === 'Select' || field.fieldtype === 'Link'"
                                    class="h-full flex items-center justify-end pr-1"
                                >
                                    <div 
                                        class="w-0 h-0 border-l-[3px] border-r-[3px] border-t-[4px] border-transparent"
                                        :style="{
                                            borderTopColor: props.form.glass_morphism_enabled 
                                                ? 'rgba(0, 0, 0, 0.5)' 
                                                : 'rgba(0, 0, 0, 0.3)',
                                        }"
                                    ></div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Empty state if no fields -->
                        <div 
                            v-if="!hasFields"
                            class="flex flex-col gap-1"
                        >
                            <div 
                                class="text-[9px] font-medium leading-tight"
                                :style="{
                                    color: props.form.glass_morphism_enabled 
                                        ? 'rgba(0, 0, 0, 0.5)' 
                                        : 'rgba(0, 0, 0, 0.4)',
                                }"
                            >
                                Field Name
                            </div>
                            <div 
                                class="h-4 rounded border w-3/4"
                                :style="{
                                    backgroundColor: props.form.glass_morphism_enabled 
                                        ? 'rgba(255, 255, 255, 0.3)' 
                                        : 'rgba(255, 255, 255, 0.8)',
                                    borderColor: props.form.glass_morphism_enabled 
                                        ? 'rgba(255, 255, 255, 0.2)' 
                                        : 'rgba(0, 0, 0, 0.08)',
                                }"
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Form Info -->
            <div class="flex flex-col gap-2 px-4 pb-4">
                <div class="flex justify-between items-start">
                    <h3 class="text-base font-medium truncate flex-1">{{ props.form.title }}</h3>
                    <Button
                        class="delete-button ml-2 flex-shrink-0"
                        variant="ghost"
                        size="sm"
                        @click.stop="showDeleteDialog = true"
                        :icon="Trash2"
                        iconOnly
                    />
                </div>
                <div class="flex gap-2 items-center">
                    <Badge
                        class="w-fit"
                        :label="props.form.is_published ? 'Published' : 'Draft'"
                        :theme="props.form.is_published ? 'green' : 'gray'"
                    />
                    <p class="text-xs text-gray-500">{{ formattedDate }}</p>
                </div>
            </div>
        </div>
        
        <Dialog
            v-model="showDeleteDialog"
            :options="{
                title: 'Delete Form',
            }"
            class="delete-dialog delete-dialog-centered"
        >
            <template #body-content>
                <p class="text-sm text-gray-600">
                    Are you sure you want to delete "{{ props.form.title }}"? This action cannot be undone.
                </p>
            </template>
            <template #actions="{ close }">
                <div class="flex gap-2 w-full">
                    <Button
                        variant="outline"
                        class="flex-1"
                        @click="close"
                        :disabled="isDeleting"
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="solid"
                        class="flex-1"
                        @click="handleDelete"
                        :loading="isDeleting"
                    >
                        Delete
                    </Button>
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
/* Scoped styles for component */
</style>

<style>
/* Global styles to ensure dialog is always centered - must be unscoped */
/* Target frappe-ui Dialog component when it has delete-dialog class */
.delete-dialog,
.delete-dialog-centered,
body > [class*="Dialog"].delete-dialog,
body > [class*="dialog"].delete-dialog,
[data-reka-popper-content-wrapper].delete-dialog,
[role="dialog"].delete-dialog {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    z-index: 9999 !important;
    margin: 0 !important;
}

/* Target dialog content wrapper - more specific selectors */
.delete-dialog [role="dialog"],
.delete-dialog .DialogContent,
.delete-dialog > div:first-child,
.delete-dialog-centered [role="dialog"],
.delete-dialog-centered .DialogContent,
.delete-dialog-centered > div:first-child,
body > [role="dialog"].delete-dialog {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    margin: 0 !important;
    max-width: 90vw !important;
    max-height: 90vh !important;
}

/* Target any element with delete-dialog class that might be the dialog container */
[class*="delete-dialog"] {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    z-index: 9999 !important;
}

/* Ensure dialog backdrop/overlay is full screen */
.delete-dialog ~ [class*="overlay"],
.delete-dialog ~ [class*="backdrop"],
.delete-dialog-centered ~ [class*="overlay"],
.delete-dialog-centered ~ [class*="backdrop"] {
    position: fixed !important;
    inset: 0 !important;
    z-index: 9998 !important;
}
</style>
