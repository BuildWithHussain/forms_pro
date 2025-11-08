<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Card } from "@/components/ui/card";
import { call } from "frappe-ui";
import { computed, ref } from "vue";
import { Trash2 } from "lucide-vue-next";
import { toast } from "vue-sonner";
import { useRouter } from "vue-router";

interface Props {
    form: {
        name: string;
        title: string;
        creation: string;
        is_published: boolean;
        background_image?: string;
        background_color?: string;
        glass_morphism_enabled?: boolean;
        overlay_opacity?: number;
        theme_color?: string;
        font_family?: string;
        logo?: string;
        fields?: Array<{
            fieldname: string;
            label: string;
            fieldtype: string;
        }>;
    };
}

const props = defineProps<Props>();

const emit = defineEmits(["deleted"]);
const router = useRouter();

const showDeleteDialog = ref(false);
const isDeleting = ref(false);

const formattedDate = computed(() => {
    const date = new Date(props.form.creation);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return "Today";
    } else if (diffDays === 1) {
        return "Yesterday";
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    }
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
    <div class="relative group">
        <Card
            @click="handleCardClick"
            class="flex flex-col gap-3 overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer"
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
            <div class="flex flex-col gap-3 px-5 pb-5">
                <div class="flex justify-between items-start gap-2">
                    <h3 class="text-base font-semibold truncate flex-1">{{ props.form.title }}</h3>
                    <Button
                        class="delete-button flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        variant="ghost"
                        size="icon"
                        @click.stop="showDeleteDialog = true"
                    >
                        <Trash2 class="h-4 w-4" />
                    </Button>
                </div>
                <div class="flex gap-3 items-center">
                    <Badge :variant="props.form.is_published ? 'default' : 'secondary'">
                        {{ props.form.is_published ? 'Published' : 'Draft' }}
                    </Badge>
                    <p class="text-xs text-muted-foreground font-medium">{{ formattedDate }}</p>
                </div>
            </div>
        </Card>
        
        <Dialog v-model:open="showDeleteDialog">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Delete Form</DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete "{{ props.form.title }}"? This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button
                        variant="outline"
                        @click="showDeleteDialog = false"
                        :disabled="isDeleting"
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        @click="handleDelete"
                        :disabled="isDeleting"
                    >
                        <span v-if="isDeleting">Deleting...</span>
                        <span v-else>Delete</span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </div>
</template>

