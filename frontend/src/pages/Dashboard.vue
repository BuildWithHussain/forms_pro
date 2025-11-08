<template>
    <DashboardLayout>
        <template #breadcrumb>Dashboard</template>
        
        <!-- Header Section -->
        <div class="flex items-center justify-between mb-8 pb-6 border-b">
            <div class="flex flex-col gap-2">
                <h1 class="text-4xl font-bold tracking-tight">Dashboard</h1>
                <p class="text-base text-muted-foreground">Manage and create forms</p>
            </div>
            <DropdownMenu>
                <DropdownMenuTrigger as-child>
                    <Button size="lg">
                        <Plus class="mr-2 h-4 w-4" />
                        Create
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuItem @click="handleCreateDraftForm">
                        <FilePlus class="mr-2 h-4 w-4" />
                        <span>Create New</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem @click="showSelectDoctypeDialog = true">
                        <Database class="mr-2 h-4 w-4" />
                        <span>Create from Existing DocType</span>
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </div>

        <!-- Statistics Section -->
        <div class="mb-8">
            <StatisticsCards />
        </div>
        
        <!-- Recents Section -->
        <div class="flex flex-col gap-4">
            <div class="flex items-center justify-between">
                <h3 class="text-xl font-semibold">Recents</h3>
            </div>
            <p class="text-sm text-muted-foreground" v-if="userForms.loading">Loading...</p>
            <Card
                v-else-if="userForms.data?.length === 0"
                class="p-12 text-center"
            >
                <CardContent class="flex flex-col items-center gap-4">
                    <FileText class="h-12 w-12 text-muted-foreground" />
                    <div>
                        <p class="text-sm font-medium">No forms created yet</p>
                        <p class="mt-1 text-xs text-muted-foreground">Get started by creating your first form</p>
                    </div>
                </CardContent>
            </Card>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" v-else>
                <FormPreviewCard 
                    v-for="form in userForms.data" 
                    :key="form.name"
                    :form="form" 
                    @deleted="userForms.reload()"
                />
            </div>
        </div>

        <!-- DocType Selection Dialog -->
        <Dialog v-model:open="showSelectDoctypeDialog">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Select DocType</DialogTitle>
                    <DialogDescription>
                        Choose a DocType to create a form from
                    </DialogDescription>
                </DialogHeader>
                <div class="flex flex-col gap-4 py-4">
                    <div class="flex flex-col gap-2">
                        <Label for="doctype">DocType</Label>
                        <Combobox
                            v-model="selectedDoctype"
                            :options="doctypes.data || []"
                            label="DocType"
                            id="doctype"
                            :loading="doctypes.loading"
                        />
                    </div>
                    <div class="flex items-center space-x-2">
                        <Checkbox
                            id="auto-populate"
                            v-model:checked="autoPopulateOnCreate"
                        />
                        <Label
                            for="auto-populate"
                            class="text-sm font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Auto-populate fields from DocType
                        </Label>
                    </div>
                    <p class="text-xs text-muted-foreground">
                        Automatically add all fields from the selected DocType to the form.
                    </p>
                </div>
                <DialogFooter>
                    <Button
                        variant="outline"
                        @click="showSelectDoctypeDialog = false"
                    >
                        Cancel
                    </Button>
                    <Button
                        :disabled="!selectedDoctype"
                        @click="handleCreateDraftFormWithDoctype"
                    >
                        Create
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import { useRouter } from "vue-router";
import { ref, onUnmounted, watch } from "vue";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Plus, FilePlus, Database, FileText } from "lucide-vue-next";
import {
    createListResource,
    createResource,
    Combobox,
} from "frappe-ui";
import { session } from "@/data/session";
import { createNewFormWithDoctype, createNewForm } from "@/utils/form_generator";
import FormPreviewCard from "@/components/dashboard/FormPreviewCard.vue";
import StatisticsCards from "@/components/dashboard/StatisticsCards.vue";
import { useEditForm } from "@/stores/editForm";

const router = useRouter();
const editFormStore = useEditForm();
const showSelectDoctypeDialog = ref(false);
const autoPopulateOnCreate = ref(true);

const handleCreateDraftFormWithDoctype = async () => {
    const data = await createNewFormWithDoctype(selectedDoctype.value);
    
    // Reset dialog state
    showSelectDoctypeDialog.value = false;
    const shouldAutoPopulate = autoPopulateOnCreate.value;
    selectedDoctype.value = null;
    
    // Navigate to edit form
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
        query: shouldAutoPopulate ? { autoPopulate: "true" } : {},
    });
};

const handleCreateDraftForm = async () => {
    const data = await createNewForm();
    router.push({
        name: "Edit Form",
        params: {
            id: data.form_document,
        },
    });
};

const userForms = createListResource({
    doctype: "Form",
    filters: {
        owner: session.user,
    },
    fields: [
        "name", 
        "title", 
        "creation", 
        "modified", 
        "is_published", 
        "route",
        "background_image",
        "background_color",
        "glass_morphism_enabled",
        "overlay_opacity",
        "theme_color",
        "font_family",
        "logo",
        "fields",
    ],
    orderBy: "modified desc",
    auto: true,
    pageLength: 9999,
});

const doctypes = createResource({
    url: "forms_pro.api.form.get_doctype_list",
    auto: true,
});
const selectedDoctype = ref(null);

// Fix z-index for Combobox dropdown when Dialog is open
let comboboxFixObserver: MutationObserver | null = null;
let comboboxFixInterval: number | null = null;

const fixComboboxZIndex = () => {
    // Only fix when dialog is open
    if (!showSelectDoctypeDialog.value) return;
    
    // Find all Combobox dropdowns (reka popper)
    document.querySelectorAll('[data-reka-popper-content-wrapper]').forEach((el) => {
        const htmlEl = el as HTMLElement;
        htmlEl.style.setProperty('z-index', '100', 'important');
        
        // Also fix the PopoverContent inside
        const popoverContent = htmlEl.querySelector('[role="dialog"], .PopoverContent, [class*="PopoverContent"]');
        if (popoverContent) {
            const popoverEl = popoverContent as HTMLElement;
            popoverEl.style.setProperty('z-index', '100', 'important');
        }
    });
};

// Watch for dialog open/close to start/stop fixing
watch(showSelectDoctypeDialog, (isOpen) => {
    if (isOpen) {
        // Start fixing when dialog opens
        fixComboboxZIndex();
        comboboxFixInterval = setInterval(fixComboboxZIndex, 50);
        
        // Watch for new dropdowns
        comboboxFixObserver = new MutationObserver(fixComboboxZIndex);
        comboboxFixObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class', 'data-reka-popper-content-wrapper'],
        });
    } else {
        // Stop fixing when dialog closes
        if (comboboxFixObserver) {
            comboboxFixObserver.disconnect();
            comboboxFixObserver = null;
        }
        if (comboboxFixInterval) {
            clearInterval(comboboxFixInterval);
            comboboxFixInterval = null;
        }
    }
});

onUnmounted(() => {
    if (comboboxFixObserver) {
        comboboxFixObserver.disconnect();
    }
    if (comboboxFixInterval) {
        clearInterval(comboboxFixInterval);
    }
});
</script>
