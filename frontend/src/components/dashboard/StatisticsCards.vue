<template>
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <!-- Total Forms Card -->
        <Card>
            <CardContent class="flex items-center gap-4 p-6">
                <div class="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                    <FileText class="w-6 h-6 text-blue-600" />
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.total ?? 0 }}
                    </p>
                    <p class="text-sm text-muted-foreground mt-1">Total Forms</p>
                </div>
            </CardContent>
        </Card>

        <!-- Published Forms Card -->
        <Card>
            <CardContent class="flex items-center gap-4 p-6">
                <div class="flex-shrink-0 w-12 h-12 rounded-lg bg-green-50 flex items-center justify-center">
                    <CheckCircle2 class="w-6 h-6 text-green-600" />
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.published ?? 0 }}
                    </p>
                    <p class="text-sm text-muted-foreground mt-1">Published</p>
                </div>
            </CardContent>
        </Card>

        <!-- Draft Forms Card -->
        <Card>
            <CardContent class="flex items-center gap-4 p-6">
                <div class="flex-shrink-0 w-12 h-12 rounded-lg bg-gray-50 flex items-center justify-center">
                    <Edit class="w-6 h-6 text-gray-600" />
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.draft ?? 0 }}
                    </p>
                    <p class="text-sm text-muted-foreground mt-1">Draft</p>
                </div>
            </CardContent>
        </Card>

        <!-- Recent Forms Card -->
        <Card>
            <CardContent class="flex items-center gap-4 p-6">
                <div class="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Clock class="w-6 h-6 text-blue-600" />
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-2xl font-bold">
                        {{ statistics.data?.recent ?? 0 }}
                    </p>
                    <p class="text-sm text-muted-foreground mt-1">Recent (7 days)</p>
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

