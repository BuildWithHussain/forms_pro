<script setup lang="ts">
import { useRouteData } from "@/stores/routeData";

const routeData = useRouteData();
</script>

<template>
    <div
        v-if="routeData.isNavigating"
        role="progressbar"
        aria-busy="true"
        aria-label="Loading"
        class="route-progress fixed top-0 left-0 right-0 h-[2px] z-[100] overflow-hidden bg-surface-gray-2"
    >
        <div class="route-progress__bar h-full bg-surface-gray-7" />
    </div>
</template>

<style scoped>
.route-progress__bar {
    width: 40%;
    animation: route-progress-slide 1.1s linear infinite;
    will-change: transform;
}
@keyframes route-progress-slide {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(350%);
    }
}
@media (prefers-reduced-motion: reduce) {
    .route-progress__bar {
        animation: none;
        width: 100%;
        opacity: 0.6;
    }
}
</style>
