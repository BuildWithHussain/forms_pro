<script setup lang="ts">
import { useRoute } from "vue-router";
import { useSubmissionForm } from "@/stores/submissionForm";
import FormHeader from "@/components/submission/FormHeader.vue";
import FormRenderer from "@/components/submission/FormRenderer.vue";
import SuccessSection from "@/components/submission/SuccessSection.vue";
import { computed } from "vue";

const route = useRoute();
const submissionFormStore = useSubmissionForm();
submissionFormStore.initialize(route.params.route as string);

// Get form styling data
const formData = computed(() => submissionFormStore.formResource?.data);

// Background styles
const backgroundStyles = computed(() => {
    if (!formData.value) return {};
    
    const styles: Record<string, string> = {};
    
    // Background image
    if (formData.value.background_image) {
        styles.backgroundImage = `url(${formData.value.background_image})`;
        styles.backgroundSize = 'cover';
        styles.backgroundPosition = 'center';
        styles.backgroundRepeat = 'no-repeat';
        styles.backgroundAttachment = 'fixed';
    }
    
    // Background color (fallback or solid)
    if (formData.value.background_color) {
        if (!formData.value.background_image) {
            styles.backgroundColor = formData.value.background_color;
        }
    } else if (!formData.value.background_image) {
        styles.backgroundColor = '#f9fafb';
    }
    
    return styles;
});

// Container styles with glass morphism
const containerStyles = computed(() => {
    if (!formData.value) return {};
    
    const styles: Record<string, string> = {};
    
    // Glass morphism effect
    if (formData.value.glass_morphism_enabled) {
        styles.backdropFilter = 'blur(10px) saturate(180%)';
        styles.webkitBackdropFilter = 'blur(10px) saturate(180%)';
        styles.backgroundColor = 'rgba(255, 255, 255, 0.75)';
        styles.border = '1px solid rgba(255, 255, 255, 0.3)';
        styles.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.2)';
    } else {
        styles.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        styles.border = '1px solid rgba(0, 0, 0, 0.1)';
        styles.boxShadow = '0 4px 16px 0 rgba(0, 0, 0, 0.1)';
    }
    
    // Overlay opacity adjustment
    if (formData.value.overlay_opacity !== undefined) {
        const opacity = formData.value.overlay_opacity;
        if (formData.value.glass_morphism_enabled) {
            styles.backgroundColor = `rgba(255, 255, 255, ${0.75 * opacity})`;
        }
    }
    
    return styles;
});

// Overlay for background image
const overlayStyles = computed(() => {
    if (!formData.value || !formData.value.background_image) return {};
    
    const opacity = formData.value.overlay_opacity || 0.5;
    return {
        backgroundColor: `rgba(0, 0, 0, ${opacity * 0.4})`
    };
});

// Theme color
const themeColor = computed(() => {
    return formData.value?.theme_color || '#3b82f6';
});
</script>
<template>
    <div class="min-h-screen w-full relative" :style="backgroundStyles">
        <!-- Background overlay -->
        <div
            v-if="formData?.background_image"
            class="absolute inset-0 z-0"
            :style="overlayStyles"
        ></div>
        
        <!-- Main content -->
        <div class="relative z-10 min-h-screen p-8">
            <div
                class="space-y-4 rounded-lg p-6 max-w-screen-md mx-auto mt-16 transition-all duration-300"
                :style="containerStyles"
            >
                <div class="space-y-4" v-if="submissionFormStore.inFormSubmission">
                    <FormHeader :theme-color="themeColor" />
                    <FormRenderer :theme-color="themeColor" />
                </div>
                <SuccessSection v-if="submissionFormStore.successSubmission" />
            </div>

            <div class="z-10 absolute bottom-0 right-0 p-8">
                <div class="flex flex-col items-end text-gray-800">
                    <span class="text-xs">Built on</span>
                    <span class="font-instrument text-xl">Forms Pro</span>
                </div>
            </div>
        </div>
    </div>
</template>
