<script setup lang="ts">
import { Settings, Plus, StretchHorizontal } from "lucide-vue-next";
import { ref, watch, computed } from "vue";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
} from "@/components/ui/sheet";
import AddFieldsSection from "@/components/builder/sidebar/AddFieldsSection.vue";
import SettingsSection from "@/components/builder/sidebar/SettingsSection.vue";
import DocTypeFieldsSection from "@/components/builder/sidebar/DoctypeFieldsSection.vue";
import { useMediaQuery } from "@vueuse/core";

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
const isMobile = useMediaQuery("(max-width: 1023px)");
const isCollapsed = ref(false);

// Track which sheet is open on mobile
const openSheetId = ref<number | null>(null);

// Computed properties for each sheet's open state
const isSettingsSheetOpen = computed({
    get: () => openSheetId.value === 0,
    set: (value) => {
        openSheetId.value = value ? 0 : null;
    },
});

const isAddFieldsSheetOpen = computed({
    get: () => openSheetId.value === 1,
    set: (value) => {
        openSheetId.value = value ? 1 : null;
    },
});

const isDocTypeFieldsSheetOpen = computed({
    get: () => openSheetId.value === 2,
    set: (value) => {
        openSheetId.value = value ? 2 : null;
    },
});

// Handle section click - on mobile open sheet, on desktop switch section
function handleSectionClick(sectionId: number) {
    if (isMobile.value) {
        // On mobile, open the sheet for this section
        openSheetId.value = openSheetId.value === sectionId ? null : sectionId;
    } else {
        // On desktop, switch the active section
        activeSection.value = sidebarSections.value[sectionId];
    }
}

// Auto-collapse on mobile
watch(isMobile, (mobile) => {
    if (mobile) {
        isCollapsed.value = true;
    } else {
        // Close any open sheets when switching to desktop
        openSheetId.value = null;
    }
});
</script>
<template>
    <TooltipProvider>
        <div
            class="form-builder-sidebar bg-sidebar border-r w-16 sm:w-80 flex flex-col h-full transition-all duration-300"
            :class="{ 'w-16': isCollapsed || isMobile, 'w-80': !isCollapsed && !isMobile }"
            data-form-builder-component="form-builder-sidebar"
        >
            <div class="h-full flex border-r border-sidebar-border">
                <div class="h-full flex flex-col gap-2 p-2 border-r border-sidebar-border bg-sidebar-accent/50 flex-shrink-0">
                    <Tooltip v-for="section in sidebarSections" :key="section.id">
                        <TooltipTrigger as-child>
                            <Button
                                variant="ghost"
                                size="icon"
                                class="h-10 w-10"
                                @click="handleSectionClick(section.id)"
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
                <!-- Desktop: Show content inline -->
                <div 
                    class="hidden lg:flex flex-col gap-4 w-full p-4 overflow-y-auto transition-all duration-300"
                    v-if="!isMobile"
                >
                    <component :is="activeSection.section" />
                </div>
            </div>
        </div>

        <!-- Mobile: Sheets for each section -->
        <Sheet :open="isSettingsSheetOpen" @update:open="isSettingsSheetOpen = $event">
            <SheetContent side="left" class="w-[85vw] sm:w-[400px] flex flex-col h-full overflow-hidden p-0">
                <SheetHeader class="flex-shrink-0 p-6 pb-4">
                    <SheetTitle>{{ sidebarSections[0].label }}</SheetTitle>
                    <SheetDescription>
                        Configure form settings and styling
                    </SheetDescription>
                </SheetHeader>
                <div class="flex-1 overflow-y-auto px-6 pb-6">
                    <SettingsSection />
                </div>
            </SheetContent>
        </Sheet>

        <Sheet :open="isAddFieldsSheetOpen" @update:open="isAddFieldsSheetOpen = $event">
            <SheetContent side="left" class="w-[85vw] sm:w-[400px] flex flex-col h-full overflow-hidden p-0">
                <SheetHeader class="flex-shrink-0 p-6 pb-4">
                    <SheetTitle>{{ sidebarSections[1].label }}</SheetTitle>
                    <SheetDescription>
                        Add new fields to your form
                    </SheetDescription>
                </SheetHeader>
                <div class="flex-1 overflow-y-auto px-6 pb-6">
                    <AddFieldsSection />
                </div>
            </SheetContent>
        </Sheet>

        <Sheet :open="isDocTypeFieldsSheetOpen" @update:open="isDocTypeFieldsSheetOpen = $event">
            <SheetContent side="left" class="w-[85vw] sm:w-[400px] flex flex-col h-full overflow-hidden p-0">
                <SheetHeader class="flex-shrink-0 p-6 pb-4">
                    <SheetTitle>{{ sidebarSections[2].label }}</SheetTitle>
                    <SheetDescription>
                        Add fields from the DocType to the form
                    </SheetDescription>
                </SheetHeader>
                <div class="flex-1 overflow-y-auto px-6 pb-6">
                    <DocTypeFieldsSection />
                </div>
            </SheetContent>
        </Sheet>
    </TooltipProvider>
</template>
