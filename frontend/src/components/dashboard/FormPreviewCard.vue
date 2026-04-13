<script setup lang="ts">
import { Badge } from "frappe-ui";
import { FileText } from "lucide-vue-next";
import { computed } from "vue";

const props = defineProps({
    form: {
        type: Object,
        required: true,
    },
});

const formattedDate = computed(() => {
    return new Date(props.form.creation).toLocaleDateString();
});
</script>
<template>
    <div
        @click="$router.push({ name: 'Manage Form', params: { id: props.form.name } })"
        class="flex flex-col gap-2 border rounded p-4 hover:border-gray-400 transition-all duration-300 cursor-pointer"
    >
        <div class="flex flex-col gap-3 text-ink-gray-6">
            <FileText class="w-5 h-5" />
            <h3 class="text-lg font-medium">{{ props.form.title }}</h3>
            <div class="flex gap-2 items-center">
                <Badge
                    class="w-fit"
                    :label="props.form.is_published ? 'Published' : 'Draft'"
                    :theme="props.form.is_published ? 'green' : 'gray'"
                />
                <p class="text-sm text-ink-gray-4">{{ formattedDate }}</p>
            </div>
        </div>
    </div>
</template>
