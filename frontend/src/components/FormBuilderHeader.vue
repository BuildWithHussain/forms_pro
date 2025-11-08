<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { 
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { ChevronDown, CloudCheck, ExternalLink, Globe, ArrowLeft } from "lucide-vue-next";
import { useEditForm } from "@/stores/editForm";
import { useRouter } from "vue-router";
import Logo from "@/assets/Logo.vue";

const router = useRouter();
const editFormStore = useEditForm();

const openFormSubmissionPage = () => {
    const routeData = router.resolve({
        name: "Form Submission Page",
        params: {
            route: editFormStore.originalFormData?.route,
        },
    });

    window.open(routeData.href, "_blank");
};
</script>
<template>
    <TooltipProvider>
        <header
            class="form-builder-header flex justify-between items-center py-2 px-4 border-b h-16 bg-background transition-all duration-300"
            data-form-builder-component="form-builder-header"
        >
            <DropdownMenu>
                <DropdownMenuTrigger as-child>
                    <Button variant="ghost" class="h-8 -ml-2 pl-2 pr-1 flex items-center justify-center gap-1">
                        <Logo />
                        <ChevronDown class="w-4 h-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                    <DropdownMenuItem @click="router.push('/')">
                        <ArrowLeft class="mr-2 h-4 w-4" />
                        <span>Go to dashboard</span>
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
            <div class="flex items-center gap-2">
                <Badge
                    v-if="editFormStore.isUnsaved"
                    variant="secondary"
                    class="bg-orange-100 text-orange-800"
                >
                    Unsaved
                </Badge>
                <Tooltip v-else>
                    <TooltipTrigger as-child>
                        <div>
                            <CloudCheck class="w-4 h-4 text-muted-foreground" />
                        </div>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Form is published</p>
                    </TooltipContent>
                </Tooltip>
                <h3 class="text-base font-medium text-foreground text-center">
                    {{ editFormStore.originalFormData?.title || "Untitled Form" }}
                </h3>
                <div class="flex items-center gap-1">
                    <span v-if="editFormStore.originalFormData?.route" class="text-base text-muted-foreground">
                        /{{ editFormStore.originalFormData?.route }}
                    </span>
                    <Tooltip>
                        <TooltipTrigger as-child>
                            <Button variant="ghost" size="icon" class="h-8 w-8" @click="openFormSubmissionPage">
                                <ExternalLink class="w-4 h-4" />
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Open in new tab</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <div v-if="editFormStore.isUnsaved">
                    <Button
                        v-if="editFormStore.isPublished"
                        @click="editFormStore.saveAndPublish"
                        :disabled="editFormStore.formResource?.loading"
                    >
                        <Globe class="mr-2 h-4 w-4" />
                        Save and publish
                    </Button>
                    <Button
                        v-else
                        @click="editFormStore.save"
                        :disabled="editFormStore.formResource?.loading"
                    >
                        Save
                    </Button>
                </div>
                <Button
                    v-else
                    :variant="editFormStore.isPublished ? 'destructive' : 'default'"
                    :disabled="editFormStore.formResource?.loading"
                    @click="editFormStore.togglePublish"
                >
                    <Globe v-if="!editFormStore.isPublished" class="mr-2 h-4 w-4" />
                    {{ editFormStore.isPublished ? 'Unpublish' : 'Publish' }}
                </Button>
            </div>
        </header>
    </TooltipProvider>
</template>
