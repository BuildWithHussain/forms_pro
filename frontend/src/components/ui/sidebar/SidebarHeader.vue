<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from "@/lib/utils"

const props = defineProps<{
  class?: HTMLAttributes["class"]
}>()
</script>

<template>
  <div
    data-sidebar="header"
    :class="cn('flex flex-col gap-2 p-2 items-center group-data-[collapsible=icon]:items-center', props.class)"
  >
    <slot />
  </div>
</template>
