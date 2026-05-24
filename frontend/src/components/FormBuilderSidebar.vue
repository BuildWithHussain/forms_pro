<script setup lang="ts">
import { Settings, Plus, StretchHorizontal } from "@lucide/vue";
import { computed, ref } from "vue";
import { Tooltip } from "frappe-ui";
import AddFieldsSection from "@/components/builder/sidebar/AddFieldsSection.vue";
import SettingsSection from "@/components/builder/sidebar/SettingsSection.vue";
import DocTypeFieldsSection from "@/components/builder/sidebar/DoctypeFieldsSection.vue";

const sidebarSections = [
    {
        id: "settings",
        label: "Settings",
        icon: Settings,
        section: SettingsSection,
    },
    {
        id: "add-fields",
        label: "Add Fields",
        icon: Plus,
        section: AddFieldsSection,
    },
    {
        id: "doctype-fields",
        label: "DocType Fields",
        icon: StretchHorizontal,
        section: DocTypeFieldsSection,
    },
];

const activeSection = ref(
    sidebarSections.find((s) => s.id === "add-fields") ?? sidebarSections[0]
);

const tabId = (id: string) => `form-builder-tab-${id}`;
const panelId = (id: string) => `form-builder-panel-${id}`;
const activeTabId = computed(() => tabId(activeSection.value.id));
const activePanelId = computed(() => panelId(activeSection.value.id));
</script>
<template>
    <div
        class="form-builder-sidebar bg-surface-white h-[calc(100dvh-3rem)] w-72 border-r border-outline-gray-1 sticky top-0 overflow-y-auto flex"
        data-form-builder-component="form-builder-sidebar"
    >
        <div
            role="tablist"
            aria-label="Form builder sections"
            aria-orientation="vertical"
            class="h-full bg-inherit flex flex-col gap-2 p-2 border-r border-outline-gray-1"
        >
            <Tooltip
                v-for="section in sidebarSections"
                :key="section.id"
                :text="section.label"
                placement="right"
            >
                <div class="relative">
                    <span
                        v-if="activeSection.id === section.id"
                        aria-hidden="true"
                        class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-0.5 rounded-full bg-surface-gray-7"
                    />
                    <Button
                        size="md"
                        role="tab"
                        :id="tabId(section.id)"
                        :aria-label="section.label"
                        :aria-selected="activeSection.id === section.id"
                        :aria-controls="panelId(section.id)"
                        @click="activeSection = section"
                        :variant="activeSection.id === section.id ? 'subtle' : 'ghost'"
                        :icon="section.icon"
                    />
                </div>
            </Tooltip>
        </div>
        <div
            role="tabpanel"
            :id="activePanelId"
            :aria-labelledby="activeTabId"
            tabindex="0"
            class="flex flex-col gap-4 w-full p-4 overflow-x-hidden focus:outline-none"
        >
            <Transition name="section-fade" mode="out-in">
                <component :is="activeSection.section" :key="activeSection.id" />
            </Transition>
        </div>
    </div>
</template>

<style scoped>
.section-fade-enter-active {
    transition: opacity 120ms ease-out;
}
.section-fade-leave-active {
    transition: opacity 120ms ease-in;
}
.section-fade-enter-from,
.section-fade-leave-to {
    opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
    .section-fade-enter-active,
    .section-fade-leave-active {
        transition: none;
    }
}
</style>
