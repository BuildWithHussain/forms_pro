<template>
	<div class="flex h-screen w-full">
		<Sidebar
			:header="{
				title: 'Forms Pro',
				subtitle: session.full_name,
				menuItems: menuItems,
			}"
			:sections="sidebarSections"
		/>
		<slot></slot>
	</div>
</template>
<script setup>
import { session } from "@/data/session";
import { ref, computed } from "vue";
import { Sidebar } from "frappe-ui";
import toggleTheme from "@/utils/theme";

const menuItems = computed(() => {
	return [
		{
			label: "Toggle Theme",
			icon: "moon",
			onClick: toggleTheme,
		},
		{
			label: "Log out",
			icon: "log-out",
			onClick: session.logout.submit,
		},
	];
});

const sidebarSections = ref([
	{
		label: "",
		items: [
			{
				label: "Dashboard",
				to: "/",
				isActive: true,
			},
		],
	},
	{
		label: "",
		items: [
			{
				label: "Submissions",
				to: "/submissions",
			},
		],
	},
]);
</script>
