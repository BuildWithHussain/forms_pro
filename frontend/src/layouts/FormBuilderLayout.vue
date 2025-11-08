<script setup lang="ts">
import FormBuilderHeader from "@/components/FormBuilderHeader.vue";
import FormBuilderSidebar from "@/components/FormBuilderSidebar.vue";
import FormBuilderContent from "@/components/FormBuilderContent.vue";
import FieldEditorSidebar from "@/components/FieldEditorSidebar.vue";
</script>
<template>
    <div class="flex flex-col h-screen">
        <FormBuilderHeader />
        <div class="flex flex-1 gap-0 overflow-hidden">
            <FormBuilderSidebar />
            <div class="flex-1 overflow-y-auto">
                <FormBuilderContent />
            </div>
            <FieldEditorSidebar />
        </div>
    </div>
</template>
