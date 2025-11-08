<template>
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <!-- Total Forms Card -->
        <Card>
            <CardContent class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <p class="text-sm font-medium text-muted-foreground">Total Forms</p>
                    <FileText class="h-4 w-4 text-muted-foreground" />
                </div>
                <div class="space-y-1">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.total ?? 0 }}
                    </p>
                </div>
            </CardContent>
        </Card>

        <!-- Published Forms Card -->
        <Card>
            <CardContent class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <p class="text-sm font-medium text-muted-foreground">Published</p>
                    <CheckCircle2 class="h-4 w-4 text-muted-foreground" />
                </div>
                <div class="space-y-1">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.published ?? 0 }}
                    </p>
                </div>
            </CardContent>
        </Card>

        <!-- Draft Forms Card -->
        <Card>
            <CardContent class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <p class="text-sm font-medium text-muted-foreground">Draft</p>
                    <Edit class="h-4 w-4 text-muted-foreground" />
                </div>
                <div class="space-y-1">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.draft ?? 0 }}
                    </p>
                </div>
            </CardContent>
        </Card>

        <!-- Recent Forms Card -->
        <Card>
            <CardContent class="p-6">
                <div class="flex items-center justify-between mb-4">
                    <p class="text-sm font-medium text-muted-foreground">Recent (7 days)</p>
                    <Clock class="h-4 w-4 text-muted-foreground" />
                </div>
                <div class="space-y-1">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.recent ?? 0 }}
                    </p>
                </div>
            </CardContent>
        </Card>
    </div>
</template>

<script setup lang="ts">
import { Card, CardContent } from "@/components/ui/card";
import { FileText, CheckCircle2, Edit, Clock } from "lucide-vue-next";
import { createResource } from "frappe-ui";

const statistics = createResource({
    url: "forms_pro.api.form.get_form_statistics",
    auto: true,
});
</script>

