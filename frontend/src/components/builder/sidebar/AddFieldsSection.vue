<script setup lang="ts">
import { ref, computed } from "vue";
import { formFields } from "@/utils/form_fields";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useEditForm } from "@/stores/editForm";
import RenderField from "@/components/RenderField.vue";
import { Plus } from "lucide-vue-next";

const search = ref("");
const componentMap = formFields.reduce((acc, field) => {
    acc[field.name] = field.component;
    return acc;
}, {});

const filteredComponents = computed(() => {
    return Object.keys(componentMap).filter((component) =>
        component.toLowerCase().includes(search.value.toLowerCase())
    );
});

const editFormStore = useEditForm();
</script>
<template>
    <div class="space-y-4">
        <h3 class="text-lg font-semibold">Add Fields</h3>
        <div class="flex flex-col gap-3">
            <Input
                v-model="search"
                type="search"
                placeholder="Search Fields"
                class="w-full"
            />
            <div v-for="component in filteredComponents" :key="component" class="relative group">
                <Card class="p-3 hover:border-primary transition-all cursor-pointer">
                    <CardContent class="p-0 flex flex-col gap-2">
                        <div class="text-sm font-medium">{{ component }}</div>
                        <RenderField class="pointer-events-none" :field="{ fieldtype: component }" />
                        <Button
                            class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity z-10 h-8 w-8"
                            variant="outline"
                            size="icon"
                            @click="editFormStore.addField(component)"
                        >
                            <Plus class="h-4 w-4" />
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    </div>
</template>
