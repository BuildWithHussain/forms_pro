<script setup lang="ts">
import { Button, createResource, Popover } from "frappe-ui";
import { session } from "@/data/session";
import { useRoute } from "vue-router";
import Avatar from "../ui/Avatar.vue";

const route = useRoute();
const brandLogo = createResource({
    url: "forms_pro.api.settings.get_brand_logo",
    auto: true,
});

const websiteSettings = createResource({
    url: "forms_pro.api.settings.get_website_settings",
    auto: true,
});

function redirectToLogin() {
    window.location.href = `/login?redirect-to=${route.fullPath}`;
}
</script>
<template>
    <div class="max-w-screen-md mx-auto flex justify-between items-center">
        <img :src="brandLogo.data" alt="Brand Logo" class="w-10 h-10" />
        <div>
            <Popover v-if="session.user">
                <template #target="{ togglePopover }">
                    <Button variant="ghost" @click="togglePopover">
                        <Avatar :userId="session.user" size="lg" />
                    </Button>
                </template>
                <template #body-main>
                    <div class="flex flex-col gap-2 bg-white rounded-lg p-2">
                        <Button
                            variant="ghost"
                            theme="red"
                            @click="session.logout.submit"
                            label="Log out"
                            icon-left="log-out"
                        />
                    </div>
                </template>
            </Popover>
            <Button v-else-if="!websiteSettings.data?.disable_sign_up" @click="redirectToLogin">
                Login
            </Button>
        </div>
    </div>
</template>
