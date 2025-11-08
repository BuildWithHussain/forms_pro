<script setup lang="ts">
import { Settings, Plus, StretchHorizontal } from "lucide-vue-next";
import { ref } from "vue";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import AddFieldsSection from "@/components/builder/sidebar/AddFieldsSection.vue";
import SettingsSection from "@/components/builder/sidebar/SettingsSection.vue";
import DocTypeFieldsSection from "@/components/builder/sidebar/DoctypeFieldsSection.vue";

const sidebarSections = ref([
    {
        id: 0,
        label: "Settings",
        icon: Settings,
        section: SettingsSection,
    },
    {
        id: 1,
        label: "Add Fields",
        icon: Plus,
        section: AddFieldsSection,
    },
    {
        id: 2,
        label: "DocType Fields",
        icon: StretchHorizontal,
        section: DocTypeFieldsSection,
    },
]);

const activeSection = ref(sidebarSections.value[1]);
</script>
<template>
    <TooltipProvider>
        <div
            class="form-builder-sidebar bg-sidebar border-r w-80 flex flex-col h-full"
            data-form-builder-component="form-builder-sidebar"
        >
            <div class="h-full flex border-r border-sidebar-border">
                <div class="h-full flex flex-col gap-2 p-2 border-r border-sidebar-border bg-sidebar-accent/50">
                    <Tooltip v-for="section in sidebarSections" :key="section.id">
                        <TooltipTrigger as-child>
                            <Button
                                variant="ghost"
                                size="icon"
                                class="h-10 w-10"
                                @click="activeSection = section"
                                :class="activeSection === section ? 'bg-sidebar-accent' : ''"
                            >
                                <component :is="section.icon" class="h-4 w-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent side="right">
                            <p>{{ section.label }}</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
                <div class="flex flex-col gap-4 w-full p-4 overflow-y-auto">
                    <component :is="activeSection.section" />
                </div>
            </div>
        </div>
    </TooltipProvider>
</template>
