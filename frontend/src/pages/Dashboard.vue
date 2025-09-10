<template>
	<BaseLayout>
		<div class="p-4 flex flex-col gap-4 w-full">
			<div class="flex flex-col gap-2">
				<h2 class="text-3xl font-bold">Dashboard</h2>
				<p class="text-base">Manage and create forms</p>
			</div>
			<Button class="w-fit" label="Create" icon-left="plus" variant="solid" />
			<div class="flex flex-col gap-2">
				<h3 class="font-medium">Recents</h3>
				<p class="text-sm text-gray-500">No forms created yet</p>
			</div>
		</div>
	</BaseLayout>
</template>

<script setup>
import BaseLayout from "@/layouts/BaseLayout.vue";
</script>
