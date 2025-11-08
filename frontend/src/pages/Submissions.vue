<template>
    <DashboardLayout>
        <template #breadcrumb>Submissions</template>
        
        <!-- Header Section -->
        <div class="flex items-center justify-between mb-8 py-6 border-b">
            <div class="flex items-center gap-4">
                <h1 class="text-4xl font-bold tracking-tight leading-tight">Submissions</h1>
                <p class="text-base text-muted-foreground leading-normal">View and manage all form submissions</p>
            </div>
            <div class="relative flex-1 max-w-sm ml-auto">
                <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    v-model="searchQuery"
                    type="search"
                    placeholder="Filter submissions..."
                    class="w-full rounded-lg bg-background pl-8"
                />
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="submissionsResource.loading" class="flex items-center justify-center py-12">
            <p class="text-sm text-muted-foreground">Loading submissions...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="submissionsResource.error" class="flex items-center justify-center py-12">
            <p class="text-sm text-destructive">Error loading submissions</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="!submissionsData || filteredSubmissions.length === 0" class="flex flex-col items-center justify-center py-12">
            <FileText class="h-12 w-12 text-muted-foreground mb-4" />
            <p class="text-sm font-medium mb-1">No submissions found</p>
            <p class="text-xs text-muted-foreground">Submissions will appear here once forms are submitted</p>
        </div>

        <!-- Submissions List -->
        <div v-else class="space-y-8">
            <div
                v-for="formData in filteredSubmissions"
                :key="formData.form.name"
                class="space-y-4"
            >
                <!-- Form Header -->
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-semibold">{{ formData.form.title }}</h2>
                        <p class="text-sm text-muted-foreground">
                            {{ formData.submissions.length }} {{ formData.submissions.length === 1 ? 'submission' : 'submissions' }}
                        </p>
                    </div>
                </div>

                <!-- Submissions Table -->
                <Card v-if="formData.submissions.length > 0">
                    <CardContent class="p-0">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead class="w-[50px]">
                                        <Checkbox
                                            :checked="isAllSelected(formData)"
                                            :indeterminate="isIndeterminate(formData)"
                                            @update:checked="(checked) => toggleSelectAll(formData, checked)"
                                        />
                                    </TableHead>
                                    <TableHead
                                        v-for="field in formData.list_view_fields"
                                        :key="field.fieldname"
                                    >
                                        {{ field.label }}
                                    </TableHead>
                                    <TableHead class="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <TableRow
                                    v-for="submission in formData.submissions"
                                    :key="submission.name"
                                    class="cursor-pointer"
                                    @click="viewSubmission(formData.form, submission)"
                                >
                                    <TableCell>
                                        <Checkbox
                                            :checked="selectedSubmissions.has(`${formData.form.name}-${submission.name}`)"
                                            @update:checked="(checked) => toggleSelection(formData.form.name, submission.name, checked)"
                                            @click.stop
                                        />
                                    </TableCell>
                                    <TableCell
                                        v-for="field in formData.list_view_fields"
                                        :key="field.fieldname"
                                    >
                                        <div class="max-w-[200px] truncate">
                                            {{ formatFieldValue(submission[field.fieldname], field.fieldtype) }}
                                        </div>
                                    </TableCell>
                                    <TableCell class="text-right" @click.stop>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger as-child>
                                                <Button variant="ghost" size="sm" class="h-8 w-8 p-0">
                                                    <MoreVertical class="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem @click="viewSubmission(formData.form, submission)">
                                                    <Eye class="mr-2 h-4 w-4" />
                                                    View
                                                </DropdownMenuItem>
                                                <DropdownMenuItem @click="deleteSubmission(formData.form, submission)">
                                                    <Trash2 class="mr-2 h-4 w-4" />
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>

                <!-- Empty State for Form -->
                <Card v-else>
                    <CardContent class="py-8">
                        <div class="text-center">
                            <p class="text-sm text-muted-foreground">No submissions for this form yet</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>

        <!-- Submission Detail Dialog -->
        <Dialog v-model:open="showDetailDialog">
            <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Submission Details</DialogTitle>
                    <DialogDescription>
                        {{ selectedForm?.title }} - {{ selectedSubmission?.name }}
                    </DialogDescription>
                </DialogHeader>
                <div v-if="detailResource.loading" class="flex items-center justify-center py-12">
                    <p class="text-sm text-muted-foreground">Loading submission details...</p>
                </div>
                <div v-else-if="detailResource.error" class="flex items-center justify-center py-12">
                    <p class="text-sm text-destructive">Error loading submission details</p>
                </div>
                <div v-else-if="submissionDetails" class="space-y-4">
                    <div
                        v-for="(value, key) in submissionDetails"
                        :key="key"
                        class="grid grid-cols-4 gap-4 py-2 border-b last:border-0"
                    >
                        <div class="font-medium text-sm">{{ formatFieldLabel(key) }}</div>
                        <div class="col-span-3 text-sm text-muted-foreground">
                            {{ formatDetailValue(value, key) }}
                        </div>
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" @click="showDetailDialog = false">
                        Close
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from "@/layouts/DashboardLayout.vue";
import { ref, computed } from "vue";
import { createResource } from "frappe-ui";
import { toast } from "vue-sonner";
import { call } from "frappe-ui";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
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
import { Input } from "@/components/ui/input";
import { FileText, Search, MoreVertical, Eye, Trash2 } from "lucide-vue-next";

interface FormData {
    form: {
        name: string;
        title: string;
        linked_doctype: string;
        route?: string;
    };
    submissions: Array<Record<string, any>>;
    list_view_fields: Array<{
        fieldname: string;
        label: string;
        fieldtype: string;
    }>;
}

const searchQuery = ref("");
const selectedSubmissions = ref<Set<string>>(new Set());
const showDetailDialog = ref(false);
const selectedForm = ref<FormData["form"] | null>(null);
const selectedSubmission = ref<Record<string, any> | null>(null);

// Load all submissions
const submissionsResource = createResource({
    url: "forms_pro.api.submission.get_all_submissions",
    auto: true,
    transform: (data: FormData[]) => {
        return data || [];
    },
});

const submissionsData = computed(() => submissionsResource.data);

// Filter submissions based on search query
const filteredSubmissions = computed(() => {
    if (!submissionsData.value) return [];
    if (!searchQuery.value.trim()) return submissionsData.value;

    const query = searchQuery.value.toLowerCase();
    return submissionsData.value
        .map((formData) => {
            // Filter submissions within each form
            const filtered = formData.submissions.filter((submission) => {
                // Search in all list view fields
                return formData.list_view_fields.some((field) => {
                    const value = submission[field.fieldname];
                    return value && String(value).toLowerCase().includes(query);
                });
            });

            return {
                ...formData,
                submissions: filtered,
            };
        })
        .filter((formData) => formData.submissions.length > 0);
});

// Load submission details
const detailResource = createResource({
    url: "forms_pro.api.submission.get_submission_details",
    auto: false,
    transform: (data: Record<string, any>) => {
        return data || {};
    },
});

const submissionDetails = computed(() => detailResource.data);

// Format field value for table display
function formatFieldValue(value: any, fieldtype: string): string {
    if (value === null || value === undefined) return "-";
    
    if (fieldtype === "Date") {
        return new Date(value).toLocaleDateString();
    }
    if (fieldtype === "Datetime" || fieldtype === "DateTime") {
        return new Date(value).toLocaleString();
    }
    if (fieldtype === "Link") {
        return value || "-";
    }
    if (fieldtype === "Check" || fieldtype === "Boolean") {
        return value ? "Yes" : "No";
    }
    
    return String(value);
}

// Format field label for detail view
function formatFieldLabel(fieldname: string): string {
    // Convert fieldname to readable label (e.g., "first_name" -> "First Name")
    return fieldname
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}

// Format detail value for detail view
function formatDetailValue(value: any, fieldname: string): string {
    if (value === null || value === undefined) return "-";
    
    // Handle dates
    if (fieldname.includes("date") || fieldname.includes("created") || fieldname.includes("modified")) {
        try {
            return new Date(value).toLocaleString();
        } catch {
            return String(value);
        }
    }
    
    // Handle booleans
    if (typeof value === "boolean") {
        return value ? "Yes" : "No";
    }
    
    // Handle objects/arrays
    if (typeof value === "object") {
        return JSON.stringify(value, null, 2);
    }
    
    return String(value);
}

// Selection helpers
function isAllSelected(formData: FormData): boolean {
    if (formData.submissions.length === 0) return false;
    return formData.submissions.every((submission) =>
        selectedSubmissions.value.has(`${formData.form.name}-${submission.name}`)
    );
}

function isIndeterminate(formData: FormData): boolean {
    const selectedCount = formData.submissions.filter((submission) =>
        selectedSubmissions.value.has(`${formData.form.name}-${submission.name}`)
    ).length;
    return selectedCount > 0 && selectedCount < formData.submissions.length;
}

function toggleSelectAll(formData: FormData, checked: boolean): void {
    formData.submissions.forEach((submission) => {
        const key = `${formData.form.name}-${submission.name}`;
        if (checked) {
            selectedSubmissions.value.add(key);
        } else {
            selectedSubmissions.value.delete(key);
        }
    });
    // Force reactivity
    selectedSubmissions.value = new Set(selectedSubmissions.value);
}

function toggleSelection(formName: string, submissionName: string, checked: boolean): void {
    const key = `${formName}-${submissionName}`;
    if (checked) {
        selectedSubmissions.value.add(key);
    } else {
        selectedSubmissions.value.delete(key);
    }
    // Force reactivity
    selectedSubmissions.value = new Set(selectedSubmissions.value);
}

// View submission details
async function viewSubmission(form: FormData["form"], submission: Record<string, any>): Promise<void> {
    selectedForm.value = form;
    selectedSubmission.value = submission;
    showDetailDialog.value = true;

    // Load submission details
    await detailResource.fetch({
        form_id: form.name,
        submission_id: submission.name,
        doctype: form.linked_doctype,
    });
}

// Delete submission
async function deleteSubmission(form: FormData["form"], submission: Record<string, any>): Promise<void> {
    if (!confirm(`Are you sure you want to delete this submission? This action cannot be undone.`)) {
        return;
    }

    try {
        await call("forms_pro.api.submission.delete_submission", {
            form_id: form.name,
            submission_id: submission.name,
            doctype: form.linked_doctype,
        });
        toast.success("Submission deleted successfully");
        submissionsResource.reload();
    } catch (error: any) {
        toast.error(error.message || "Failed to delete submission");
    }
}
</script>

