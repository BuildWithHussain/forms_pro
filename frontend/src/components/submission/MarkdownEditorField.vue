<template>
    <div class="markdown-editor-field-wrapper">
        <div class="border rounded-md">
            <div class="flex border-b">
                <button
                    :class="[
                        'px-4 py-2 text-sm font-medium',
                        viewMode === 'edit' ? 'bg-muted border-b-2 border-primary' : 'text-muted-foreground hover:text-foreground'
                    ]"
                    @click="viewMode = 'edit'"
                >
                    Edit
                </button>
                <button
                    :class="[
                        'px-4 py-2 text-sm font-medium',
                        viewMode === 'preview' ? 'bg-muted border-b-2 border-primary' : 'text-muted-foreground hover:text-foreground'
                    ]"
                    @click="viewMode = 'preview'"
                >
                    Preview
                </button>
            </div>
            <Textarea
                v-if="viewMode === 'edit'"
                :model-value="markdownValue"
                @update:model-value="handleInput"
                variant="outline"
                :placeholder="props.field.placeholder || 'Enter markdown...'"
                rows="10"
                class="font-mono text-sm border-0 rounded-none"
            />
            <div
                v-else
                class="p-4 prose prose-sm max-w-none"
                v-html="renderedMarkdown"
            ></div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { Textarea } from 'frappe-ui';
import { FormField } from '@/types/formfield';

const props = defineProps<{
    field: FormField;
    modelValue: string | null;
}>();

const emit = defineEmits<{
    'update:modelValue': [value: string | null];
}>();

const markdownValue = ref(props.modelValue || '');
const viewMode = ref<'edit' | 'preview'>('edit');

watch(() => props.modelValue, (value) => {
    markdownValue.value = value || '';
}, { immediate: true });

function handleInput(value: string) {
    markdownValue.value = value;
    emit('update:modelValue', value || null);
}

// Simple markdown to HTML converter (basic implementation)
const renderedMarkdown = computed(() => {
    if (!markdownValue.value) return '';
    
    let html = markdownValue.value;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2">$1</a>');
    
    // Code blocks
    html = html.replace(/```([^`]+)```/gim, '<pre><code>$1</code></pre>');
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');
    
    // Line breaks
    html = html.replace(/\n/gim, '<br>');
    
    return html;
});
</script>

<style scoped>
.markdown-editor-field-wrapper :deep(textarea) {
    font-family: 'Courier New', Courier, monospace;
}
</style>

