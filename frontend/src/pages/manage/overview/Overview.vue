<script setup lang="ts">
import AccessSection from "@/components/form/manage/AccessSection.vue";
import { useManageForm } from "@/stores/form/manageForm";
import { FileText, CaseLower, Lock } from "lucide-vue-next";
import { formatPrettyDate } from "@/utils/date";
import { TabButtons, LoadingText } from "frappe-ui";
import Avatar from "@/components/ui/Avatar.vue";
import { useQueryParam } from "@/composables/useQueryParam";

const manageFormStore = useManageForm();

const tabs = [
    {
        label: "Description",
        iconLeft: CaseLower,
        value: "description",
    },
    {
        label: "Access",
        iconLeft: Lock,
        value: "shared",
    },
] as const;

// Extract tab value type from tabs array - automatically includes all tab values
type TabValue = typeof tabs[number]["value"];
const validTabValues: TabValue[] = tabs.map((t) => t.value);
const selectedTab = useQueryParam<TabValue>("tab", "description", validTabValues);
</script>

<template>
    <div v-if="manageFormStore.formResource.loading">
        <LoadingText />
    </div>
    <div v-if="manageFormStore.formResource.isFinished">
        <div class="flex flex-col gap-3">
            <div class="flex gap-3 justify-between items-center">
                <div class="flex gap-3 items-center text-ink-gray-8">
                    <FileText class="w-6 h-6" />
                    <h2 class="text-3xl font-bold">{{ manageFormStore.formData?.title }}</h2>
                </div>
                <div class="flex gap-3">
                    <Button
                        @click="
                            $router.push({
                                name: 'Edit Form',
                                params: { id: manageFormStore.formData?.name },
                            })
                        "
                        class="w-24"
                        size="md"
                        label="Edit"
                        variant="solid"
                        icon-left="edit-2"
                    />
                </div>
            </div>
            <div class="flex flex-col gap-2 text-ink-gray-5">
                <div class="flex gap-2 items-center text-xs">
                    <p>Modified {{ formatPrettyDate(manageFormStore.formData?.modified) }}</p>
                    <span>•</span>
                    <p>Created {{ formatPrettyDate(manageFormStore.formData?.creation) }} by</p>
                    <Avatar :userId="manageFormStore.formData?.owner" />
                </div>
            </div>
            <TabButtons class="w-fit mb-2" :buttons="tabs" v-model="selectedTab" />
            <DescriptionSection v-if="selectedTab === 'description'" />
            <AccessSection v-if="selectedTab === 'shared'" />
        </div>
    </div>
</template>
