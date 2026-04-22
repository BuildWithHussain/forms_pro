<script setup lang="ts">
import { Settings, Plus, StretchHorizontal } from "@lucide/vue";
import { ref } from "vue";
import { Tooltip } from "frappe-ui";
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
    <div
        class="form-builder-sidebar bg-primary h-[calc(100vh-3rem)] w-72 border-r sticky top-0 overflow-y-auto flex"
        data-form-builder-component="form-builder-sidebar"
    >
        <div class="h-full bg-inherit flex flex-col gap-2 p-2 border-r">
            <Tooltip
                v-for="section in sidebarSections"
                :key="section.id"
                :text="section.label"
                placement="right"
            >
                <Button
                    size="md"
                    @click="activeSection = section"
                    :variant="activeSection === section ? 'subtle' : 'ghost'"
                    :icon="section.icon"
                />
            </Tooltip>
        </div>
        <div class="flex flex-col gap-4 w-full p-4 overflow-x-hidden">
            <component :is="activeSection.section" />
        </div>
    </div>
</template>
