<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { session } from "@/data/session";
import { useRouter } from "vue-router";
import { LayoutDashboard, LogOut, FolderTree } from "lucide-vue-next";
const router = useRouter();

// App logo from hooks.py
const appLogo = "/assets/forms_pro/formpro.png";

const handleLogout = () => {
  session.logout.submit();
};

const menuItems = [
  {
    title: "Dashboard",
    icon: LayoutDashboard,
    to: "/",
  },
  {
    title: "Categories",
    icon: FolderTree,
    to: "/categories",
  },
];
</script>

<template>
  <Sidebar collapsible="icon">
    <SidebarHeader>
      <div class="flex items-center gap-2 px-2 py-2 group justify-start group-data-[collapsible=icon]:justify-center w-full">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg overflow-hidden flex-shrink-0">
          <img 
            :src="appLogo" 
            alt="Forms Pro" 
            class="h-full w-full object-contain"
          />
        </div>
        <div class="flex flex-col group-data-[collapsible=icon]:hidden transition-opacity duration-200">
          <span class="text-sm font-semibold whitespace-nowrap">Forms Pro</span>
          <span class="text-xs text-muted-foreground whitespace-nowrap">{{ session.full_name }}</span>
        </div>
      </div>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Navigation</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in menuItems" :key="item.title">
              <SidebarMenuButton
                :as-child="true"
                :is-active="router.currentRoute.value.path === item.to"
              >
                <router-link :to="item.to" class="flex items-center gap-2">
                  <component :is="item.icon" class="h-4 w-4 shrink-0" />
                  <span class="whitespace-nowrap">{{ item.title }}</span>
                </router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton @click="handleLogout">
            <LogOut class="h-4 w-4 shrink-0" />
            <span class="whitespace-nowrap">Log out</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
  </Sidebar>
</template>

