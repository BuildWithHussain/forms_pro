<template>
    <DashboardLayout>
        <template #breadcrumb>Categories</template>
        
        <!-- Header Section -->
        <div class="flex items-center justify-between mb-8 py-6 border-b">
            <div class="flex items-center gap-4">
                <h1 class="text-4xl font-bold tracking-tight leading-tight">Categories</h1>
                <p class="text-base text-muted-foreground leading-normal">Organize your forms into categories</p>
            </div>
            <Button size="lg" @click="showCreateDialog = true">
                <Plus class="mr-2 h-4 w-4" />
                Create Category
            </Button>
        </div>

        <!-- Categories List -->
        <div v-if="categoriesResource.loading" class="flex items-center justify-center py-12">
            <p class="text-sm text-muted-foreground">Loading categories...</p>
        </div>

        <div v-else-if="categoriesResource.error" class="flex items-center justify-center py-12">
            <p class="text-sm text-destructive">Error loading categories</p>
        </div>

        <div v-else-if="!categoriesData || categoriesData.length === 0" class="flex flex-col items-center justify-center py-12">
            <FolderTree class="h-12 w-12 text-muted-foreground mb-4" />
            <p class="text-sm font-medium mb-1">No categories yet</p>
            <p class="text-xs text-muted-foreground mb-4">Create your first category to organize your forms</p>
            <Button @click="showCreateDialog = true">
                <Plus class="mr-2 h-4 w-4" />
                Create Category
            </Button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card
                v-for="category in categoriesData"
                :key="category.name || 'uncategorized'"
                class="relative"
            >
                <CardHeader>
                    <div class="flex items-start justify-between">
                        <div class="flex items-center gap-3 flex-1">
                            <div
                                v-if="category.color"
                                class="h-4 w-4 rounded-full flex-shrink-0"
                                :style="{ backgroundColor: category.color }"
                            ></div>
                            <div class="flex-1 min-w-0">
                                <CardTitle class="text-lg">{{ category.title }}</CardTitle>
                                <p v-if="category.description" class="text-sm text-muted-foreground mt-1 line-clamp-2">
                                    {{ category.description }}
                                </p>
                            </div>
                        </div>
                        <DropdownMenu v-if="category.name">
                            <DropdownMenuTrigger as-child>
                                <Button variant="ghost" size="sm" class="h-8 w-8 p-0">
                                    <MoreVertical class="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem @click="editCategory(category)">
                                    <Edit class="mr-2 h-4 w-4" />
                                    Edit
                                </DropdownMenuItem>
                                <DropdownMenuItem @click="deleteCategory(category)" class="text-destructive">
                                    <Trash2 class="mr-2 h-4 w-4" />
                                    Delete
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </CardHeader>
                <CardContent>
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-2">
                            <Badge variant="secondary">
                                {{ category.form_count || 0 }} {{ category.form_count === 1 ? 'form' : 'forms' }}
                            </Badge>
                        </div>
                    </div>
                    
                    <!-- Forms List -->
                    <div v-if="category.forms && category.forms.length > 0" class="space-y-2">
                        <div
                            v-for="form in category.forms"
                            :key="form.name"
                            class="flex items-center justify-between p-2 rounded-md border hover:bg-accent transition-colors"
                        >
                            <div class="flex items-center gap-2 flex-1 min-w-0">
                                <FileText class="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm font-medium truncate">{{ form.title }}</p>
                                    <p class="text-xs text-muted-foreground">
                                        {{ formatDate(form.modified) }}
                                    </p>
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <Badge v-if="form.is_published" variant="default" class="text-xs">
                                    Published
                                </Badge>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    @click="goToForm(form.name)"
                                >
                                    <ExternalLink class="h-3 w-3" />
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div v-else class="text-center py-4">
                        <p class="text-sm text-muted-foreground">No forms in this category</p>
                    </div>
                </CardContent>
            </Card>
        </div>

        <!-- Create/Edit Category Dialog -->
        <Dialog v-model:open="showCreateDialog">
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{{ editingCategory ? 'Edit Category' : 'Create Category' }}</DialogTitle>
                    <DialogDescription>
                        {{ editingCategory ? 'Update category details' : 'Add a new category to organize your forms' }}
                    </DialogDescription>
                </DialogHeader>
                <div class="flex flex-col gap-4 py-4">
                    <div class="flex flex-col gap-2">
                        <Label for="category-title">Title *</Label>
                        <Input
                            id="category-title"
                            v-model="categoryForm.title"
                            placeholder="e.g., Customer Forms"
                            required
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <Label for="category-description">Description</Label>
                        <Textarea
                            id="category-description"
                            v-model="categoryForm.description"
                            placeholder="Optional description for this category"
                            rows="3"
                        />
                    </div>
                    <div class="flex flex-col gap-2">
                        <Label for="category-color">Color</Label>
                        <div class="flex items-center gap-2">
                            <Input
                                id="category-color"
                                v-model="categoryForm.color"
                                type="color"
                                class="w-16 h-10"
                            />
                            <Input
                                v-model="categoryForm.color"
                                placeholder="#3b82f6"
                                pattern="^#[0-9A-Fa-f]{6}$"
                            />
                        </div>
                        <p class="text-xs text-muted-foreground">Hex color code for category display</p>
                    </div>
                    <div class="flex flex-col gap-2">
                        <Label for="category-order">Order</Label>
                        <Input
                            id="category-order"
                            v-model.number="categoryForm.order"
                            type="number"
                            placeholder="Display order (lower numbers appear first)"
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button
                        variant="outline"
                        @click="cancelEdit"
                    >
                        Cancel
                    </Button>
                    <Button
                        :disabled="!categoryForm.title"
                        @click="saveCategory"
                    >
                        {{ editingCategory ? 'Update' : 'Create' }}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import { useRouter } from "vue-router";
import { ref, computed, watch } from "vue";
import { createResource } from "frappe-ui";
import { toast } from "vue-sonner";
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, FolderTree, MoreVertical, Edit, Trash2, FileText, ExternalLink } from "lucide-vue-next";
import { call } from "frappe-ui";

const router = useRouter();

const showCreateDialog = ref(false);
const editingCategory = ref<any>(null);

const categoryForm = ref({
    title: "",
    description: "",
    color: "#3b82f6",
    order: null as number | null,
});

// Load categories with forms
const categoriesResource = createResource({
    url: "forms_pro.api.category.get_forms_by_category",
    auto: true,
    transform: (data: any) => {
        return data || [];
    },
});

const categoriesData = computed(() => categoriesResource.data);

const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
};

const saveCategory = async () => {
    if (!categoryForm.value.title) {
        toast.error("Title is required");
        return;
    }

    try {
        if (editingCategory.value) {
            await call("forms_pro.api.category.update_category", {
                category_id: editingCategory.value.name,
                title: categoryForm.value.title,
                description: categoryForm.value.description || null,
                color: categoryForm.value.color || null,
                order: categoryForm.value.order || null,
            });
            toast.success("Category updated successfully");
        } else {
            await call("forms_pro.api.category.create_category", {
                title: categoryForm.value.title,
                description: categoryForm.value.description || null,
                color: categoryForm.value.color || null,
                order: categoryForm.value.order || null,
            });
            toast.success("Category created successfully");
        }
        
        showCreateDialog.value = false;
        cancelEdit();
        categoriesResource.reload();
    } catch (error: any) {
        toast.error(error.message || "Failed to save category");
    }
};

const editCategory = (category: any) => {
    editingCategory.value = category;
    categoryForm.value = {
        title: category.title || "",
        description: category.description || "",
        color: category.color || "#3b82f6",
        order: category.order || null,
    };
    showCreateDialog.value = true;
};

const deleteCategory = async (category: any) => {
    if (!confirm(`Are you sure you want to delete "${category.title}"?`)) {
        return;
    }

    try {
        await call("forms_pro.api.category.delete_category", {
            category_id: category.name,
        });
        toast.success("Category deleted successfully");
        categoriesResource.reload();
    } catch (error: any) {
        toast.error(error.message || "Failed to delete category");
    }
};

const cancelEdit = () => {
    editingCategory.value = null;
    categoryForm.value = {
        title: "",
        description: "",
        color: "#3b82f6",
        order: null,
    };
};

const goToForm = (formId: string) => {
    router.push({
        name: "Edit Form",
        params: { id: formId },
    });
};

watch(showCreateDialog, (isOpen) => {
    if (!isOpen) {
        cancelEdit();
    }
});
</script>

