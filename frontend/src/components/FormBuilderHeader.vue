<script setup lang="ts">
import { Badge, Popover, Tooltip } from "frappe-ui";
import { ChevronDown, CloudCheck, ExternalLink, CloudOff } from "lucide-vue-next";
import { Button } from "frappe-ui";
import { useEditForm } from "@/stores/editForm";
import { useRouter } from "vue-router";
import Logo from "@/assets/Logo.vue";

const router = useRouter();
const editFormStore = useEditForm();

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
    const routeRecord = router.getRoutes().find((r) => r.name === "Form Submission Page");
    if (!routeRecord) return;

    const path = routeRecord.path.replace(":route(.*)", route);
    const routeData = router.resolve(path);

    window.open(routeData.href, "_blank");
};
</script>
<template>
    <header
        class="form-builder-header flex justify-between items-center py-2 px-4 border-b h-[3rem] transition-all duration-300"
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
        <div class="flex items-center gap-2">
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
            <Tooltip
                v-else-if="!editFormStore.isPublished"
                text="Form is not published"
                placement="bottom"
            >
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
            <div v-if="editFormStore.isUnsaved">
                <Button
                    v-if="editFormStore.isPublished"
                    label="Save and publish"
                    icon-left="globe"
                    variant="solid"
                    @click="editFormStore.saveAndPublish"
                    :loading="editFormStore.formResource?.loading"
                />
                <Button
                    v-else
                    label="Save"
                    variant="solid"
                    @click="editFormStore.save"
                    :loading="editFormStore.formResource?.loading"
                />
            </div>
            <Button
                v-else
                :label="editFormStore.isPublished ? 'Unpublish' : 'Publish'"
                :icon-left="editFormStore.isPublished ? '' : 'globe'"
                :variant="editFormStore.isPublished ? 'subtle' : 'solid'"
                :theme="editFormStore.isPublished ? 'red' : 'gray'"
                :loading="editFormStore.formResource?.loading"
                @click="editFormStore.togglePublish"
            />
        </div>
    </header>
</template>
