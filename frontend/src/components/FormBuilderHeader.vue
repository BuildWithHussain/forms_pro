<script setup lang="ts">
import { Badge, Button, Popover, Tooltip, type ButtonProps } from "frappe-ui";
import { TextMorph } from "torph/vue";
import { ChevronDown, CloudCheck, ExternalLink, CloudOff } from "@lucide/vue";
import { useEditForm } from "@/stores/editForm";
import { useRouter } from "vue-router";
import { computed, nextTick, ref, watch } from "vue";
import Logo from "@/assets/Logo.vue";

const router = useRouter();
const editFormStore = useEditForm();

const SUBMISSION_ROUTE_NAME = "Form Submission Page";

type ActionConfig = {
    label: string;
    iconLeft: string;
    variant: ButtonProps["variant"];
    theme: ButtonProps["theme"];
    handler: () => unknown;
};

function computeConfig(): ActionConfig {
    if (editFormStore.isUnsaved && editFormStore.isPublished)
        return {
            label: "Save and publish",
            iconLeft: "globe",
            variant: "solid",
            theme: "gray",
            handler: editFormStore.saveAndPublish,
        };
    if (editFormStore.isUnsaved)
        return {
            label: "Save",
            iconLeft: "",
            variant: "solid",
            theme: "gray",
            handler: editFormStore.save,
        };
    if (editFormStore.isPublished)
        return {
            label: "Unpublish",
            iconLeft: "",
            variant: "subtle",
            theme: "red",
            handler: editFormStore.togglePublish,
        };
    return {
        label: "Publish",
        iconLeft: "globe",
        variant: "solid",
        theme: "gray",
        handler: editFormStore.togglePublish,
    };
}

const frozenConfig = ref<ActionConfig | null>(null);
const buttonConfig = computed<ActionConfig>(() => frozenConfig.value ?? computeConfig());

watch(
    () => editFormStore.formResource,
    (r) => {
        if (!r) frozenConfig.value = null;
    }
);

async function onAction() {
    if (frozenConfig.value) return;
    frozenConfig.value = computeConfig();
    try {
        await frozenConfig.value.handler();
        await nextTick();
    } catch {
        // save() rejects on duplicate fieldnames / no-changes; togglePublish surfaces errors via toast
    } finally {
        frozenConfig.value = null;
    }
}

const openFormSubmissionPage = () => {
    const route = editFormStore.originalFormData?.route;
    if (!route) return;

    // Why router.resolve() with named route + params doesn't work:
    // Vue Router URL-encodes parameter values when using the params object,
    // even with catch-all routes. So a route like "s/something" becomes "s%2Fsomething".
    //
    // Solution: Get the route definition and construct the path manually,
    // then use router.resolve() with the path string (which doesn't get encoded).
    // This way, if the path changes in router.ts, this code still works.
    const routeRecord = router.getRoutes().find((r) => r.name === SUBMISSION_ROUTE_NAME);
    if (!routeRecord) return;

    const path = routeRecord.path.replace(/:\w+\(.*?\)/, route);
    const routeData = router.resolve(path);

    window.open(routeData.href, "_blank");
};
</script>
<template>
    <header
        class="form-builder-header flex justify-between items-center py-2 px-4 border-b h-[3rem]"
        data-form-builder-component="form-builder-header"
    >
        <Popover>
            <template #target="{ togglePopover }">
                <button class="flex items-center gap-1" @click="togglePopover">
                    <Logo />
                    <ChevronDown class="w-5 h-5" />
                </button>
            </template>
            <template #body-main>
                <div class="flex flex-col gap-2 bg-white rounded-lg p-2">
                    <Button
                        label="Go Back"
                        icon-left="arrow-left"
                        variant="ghost"
                        @click="
                            router.replace({
                                name: 'Manage Form',
                                params: {
                                    id: editFormStore.originalFormData?.name,
                                },
                            })
                        "
                    />
                </div>
            </template>
        </Popover>
        <div class="flex items-center gap-2 m-auto">
            <Badge
                v-if="editFormStore.isUnsaved"
                variant="subtle"
                label="Unsaved"
                theme="orange"
                size="sm"
            />
            <Tooltip
                v-else-if="editFormStore.isPublished"
                text="Form is published"
                placement="bottom"
            >
                <CloudCheck class="w-4 h-4 text-gray-500" />
            </Tooltip>
            <Tooltip v-else text="Form is not published" placement="bottom">
                <CloudOff class="w-4 h-4 text-gray-500" />
            </Tooltip>
            <h3 class="text-base font-medium text-gray-600 text-center">
                {{ editFormStore.originalFormData?.title || "Untitled Form" }}
            </h3>
            <div class="flex items-center gap-1">
                <span v-if="editFormStore.originalFormData?.route" class="text-base text-gray-600">
                    /{{ editFormStore.originalFormData?.route }}
                </span>
                <Tooltip text="Open in new tab" placement="bottom">
                    <Button variant="ghost" @click="openFormSubmissionPage">
                        <ExternalLink class="w-4 h-4 text-gray-500" />
                    </Button>
                </Tooltip>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <Button
                :aria-label="buttonConfig.label"
                :icon-left="buttonConfig.iconLeft"
                :variant="buttonConfig.variant"
                :theme="buttonConfig.theme"
                :loading="editFormStore.isSaving || editFormStore.isLoading"
                @click="onAction"
            >
                <TextMorph :text="buttonConfig.label" />
            </Button>
        </div>
    </header>
</template>
